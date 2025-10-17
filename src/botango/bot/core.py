import hmac
import logging
import sys
from typing import Optional

import aiohttp
from aiogram import Bot, Router
from aiogram import Dispatcher as _Dispatcher
from aiogram.loggers import event
from aiogram.types import Update
from aiohttp import web, ClientSession
from aiohttp.web_response import Response


class _BaseWebSettings:
    def __init__(
            self,
            bot: Bot,
            dispatcher: Optional[_Dispatcher] = None,
            drop_pending_updates: bool = True,
            is_logging: bool = True
    ):
        self._bot = bot
        self._dispatcher = dispatcher or _Dispatcher()
        self._drop_pending_updates = drop_pending_updates
        if is_logging:
            self._logging()

    @property
    def dispatcher(self) -> _Dispatcher:
        return self._dispatcher

    @property
    def bot(self) -> Bot:
        return self._bot

    def include_router(self, router: Router):
        self._dispatcher.include_router(router)

    def include_routers(self, *routers: Router):
        self._dispatcher.include_routers(*routers)

    @staticmethod
    def _logging():
        event.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        event.addHandler(handler)

class LongPollingBot(_BaseWebSettings):
    async def run(self):
        try:
            await self.bot.delete_webhook(drop_pending_updates=self._drop_pending_updates)
            await self.dispatcher.start_polling(self._bot)
        finally:
            await self.bot.session.close()

class WebhookBot(_BaseWebSettings):
    def __init__(
        self,
        bot: Bot,
        base_url: str | None,
        webhook_secret: str,
        webhook_path: str = "/telegram/webhook",
        dispatcher: Optional[_Dispatcher] = None,
        *,
        allowed_updates: list[str] | None = None,
        drop_pending_updates: bool = True,
        turn_logging: bool = True,
    ):
        super().__init__(bot=bot, dispatcher=dispatcher, drop_pending_updates=drop_pending_updates)

        self.app = web.Application(client_max_size=1024*1024)

        self._webhook_secret = webhook_secret
        self._webhook_path = webhook_path if webhook_path.startswith("/") else f"/{webhook_path}"
        self._allowed_updates = allowed_updates
        self._base_url = base_url  # может быть None — тогда возьмём из ngrok
        self._webhook_url = None  # вычислим на старте


        if turn_logging:
            self._logging()

    async def _resolve_public_base_url(self) -> str:
        if not self._base_url:
            raise AttributeError("Base url can't be empty!")
        return self._base_url.rstrip("/")

    async def _handle(self, request: web.Request) -> Response:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not header_secret or not hmac.compare_digest(header_secret, self._webhook_secret):
            return web.Response(status=403)
        try:
            data = await request.json()
        except Exception as e:
            event.exception("Invalid JSON on webhook: %s", e)
            return web.json_response({"ok": False, "error": "invalid json"}, status=200)

        try:
            update = Update.model_validate(data, context={"bot": self.bot})
            await self.dispatcher.feed_update(self.bot, update)
        except Exception:
            event.exception("Update handling failed")
            return web.json_response({"ok": True})
        return web.json_response({"ok": True})

    async def _on_startup(self, app: web.Application):
        self.app["http_session"] = ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        base = await self._resolve_public_base_url()
        self._webhook_url = f"{base}{self._webhook_path}"

        if self._allowed_updates is None or not isinstance(self._allowed_updates, list):
            self._allowed_updates = ["message", "callback_query"]

        await self.bot.set_webhook(
            url=self._webhook_url,
            secret_token=self._webhook_secret,
            allowed_updates=self._allowed_updates,
            drop_pending_updates=self._drop_pending_updates,
        )
        # хук жизненного цикла aiogram v3
        try:
            await self.dispatcher.emit_startup(self.bot)
        except AttributeError:
            pass

    async def _on_cleanup(self, app: web.Application):
        try:
            await self.dispatcher.emit_shutdown()
        except AttributeError:
            pass
        await self.bot.delete_webhook()
        await self.app["http_session"].close()

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        self.app.router.add_post(self._webhook_path, self._handle)

        async def _health(_):
            return web.json_response({
                "status": "ok",
                "webhook_url": self._webhook_url,
            })

        self.app.router.add_get("/healthz", _health)
        self.app.on_startup.append(self._on_startup) # type: ignore
        self.app.on_cleanup.append(self._on_cleanup) # type: ignore
        web.run_app(self.app, host=host, port=port)

import asyncio

import click
from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError


def check_token(token):
    async def _check_token():
        bot = Bot(token)
        async with bot:
            try:
                me = await bot.get_me()
                click.echo(f"✅ Токен действителен. Это бот @{me.username}")
            except TelegramUnauthorizedError:
                raise click.ClickException("❌ Токен недействителен. Telegram вернул ошибку авторизации.")
            finally:
                await bot.session.close()
    asyncio.run(_check_token())
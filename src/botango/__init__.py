"""botango — удобные утилиты для Telegram-ботов


Экспортируем основное API и версию пакета.
"""


__all__ = ["__version__", "LongPollingBot"]
__version__ = "0.1.0"

from botango.bot.core_bot import LongPollingBot
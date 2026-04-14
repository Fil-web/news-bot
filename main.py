import asyncio
import os
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from command.handlers import callback_router, command_router, text_router
from news.service import news_store
from utils.logger import logger

load_dotenv()

TOKEN = os.getenv("TOKEN")
PARSER_INTERVAL_HOURS = int(os.getenv("PARSER_INTERVAL_HOURS", "6"))

if not TOKEN:
    raise RuntimeError("Переменная окружения TOKEN не задана.")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(command_router)
dp.include_router(callback_router)
dp.include_router(text_router)


async def parser_scheduler() -> None:
    interval_seconds = PARSER_INTERVAL_HOURS * 60 * 60
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            await news_store.refresh()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Ошибка фонового обновления новостей: %s", exc)


async def main() -> None:
    await news_store.initialize()
    scheduler_task = asyncio.create_task(parser_scheduler(), name="news-parser-scheduler")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

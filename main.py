# main.py
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import os
from dotenv import load_dotenv
from command.handlers import command_router, callback_router, text_router

# Загружаем переменные окружения
load_dotenv()

# Чтение токена из .env
TOKEN = os.getenv("TOKEN")

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключение роутеров
dp.include_router(command_router)
dp.include_router(callback_router)
dp.include_router(text_router)

# Запуск бота
async def main():
    await dp.start_polling(bot)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
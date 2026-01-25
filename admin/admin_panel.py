# command/admin.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаём роутер для админ-команд
admin_router = Router()

# Чтение ADMIN_IDS из .env
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS").split(',')))  # Преобразуем строку в множество чисел

# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Клавиатура админ-панели
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Управление пользователями")],
        [KeyboardButton(text="📂 Логи")],
        [KeyboardButton(text="🚪 Закрыть админ-панель")],
    ],
    resize_keyboard=True
)

# Команда /admin
@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав доступа.")
        return

    await message.answer("Админ-панель:", reply_markup=admin_keyboard)
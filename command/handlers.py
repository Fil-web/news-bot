from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.logger import logger
from database.database import create_connection, create_table, add_reaction, get_reaction
import pandas as pd
import asyncio
import os

# Создаём роутеры
command_router = Router()  # Роутер для команд
callback_router = Router()  # Роутер для callback-запросов
text_router = Router()  # Роутер для текстовых сообщений

# Чтение данных из Excel-файла
df = pd.read_excel("database/book.xlsx")
df = df.fillna("Нет данных")
df = df.drop_duplicates()

# Подключение к базе данных
conn = create_connection("database/reactions.db")
if conn is not None:
    create_table(conn)  # Создаем таблицу, если её нет

# Inline-кнопки для главного меню
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📰 Новости", callback_data="news"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
    ],
    [
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
    ]
])

# Reply-кнопки для главного меню
reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📰 Новости"),
            KeyboardButton(text="📊 Статистика"),
        ],
        [
            KeyboardButton(text="ℹ️ Помощь"),
        ]
    ],
    resize_keyboard=True
)

# Команда /start
@command_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=reply_keyboard
    )

# Обработка Inline-кнопок
@callback_router.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    if data == "news":
        await send_news_to_telegram(callback.message.chat.id, callback.bot, 0)  # Начинаем с первой новости
    elif data == "stats":
        await callback.message.answer(f"Всего новостей: {len(df)}")
    elif data == "help":
        # Статический ответ вместо GigaChat
        await callback.message.answer("Используйте кнопки для навигации. 📰 Новости - читайте новости, 📊 Статистика - узнайте количество новостей.")
    elif data.startswith("like_"):
        await handle_like_dislike(callback, "like")
    elif data.startswith("dislike_"):
        await handle_like_dislike(callback, "dislike")
    await callback.answer()

# Обработка текстовых сообщений
@text_router.message()
async def handle_text(message: types.Message):
    text = message.text
    if text == "📰 Новости":
        await send_news_to_telegram(message.chat.id, message.bot, 0)  # Начинаем с первой новости
    elif text == "📊 Статистика":
        await message.answer(f"Всего новостей: {len(df)}")
    elif text == "ℹ️ Помощь":
        # Статический ответ вместо GigaChat
        await message.answer("Используйте кнопки для навигации. 📰 Новости - читайте новости, 📊 Статистика - узнайте количество новостей.")

# Функция для отправки новостей
async def send_news_to_telegram(chat_id: int, bot, news_index: int):
    try:
        if not all(col in df.columns for col in ['Заголовок', 'Описание', 'Ссылка']):
            logger.error("В Excel-файле отсутствуют необходимые столбцы.")
            return

        # Проверяем, что индекс новости находится в пределах данных
        if news_index >= len(df):
            await bot.send_message(chat_id=chat_id, text="Новости закончились.")
            return

        # Получаем текущую новость
        row = df.iloc[news_index]

        # Создаем клавиатуру с кнопками "👍" и "👎"
        like_dislike_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like_{news_index}"),
                InlineKeyboardButton(text="👎", callback_data=f"dislike_{news_index}"),
            ]
        ])

        message = (
            f"📰 <b>Заголовок:</b> {row['Заголовок']}\n"
            f"📝 <b>Описание:</b> {row['Описание']}\n"
            f"🔗 <b>Ссылка:</b> {row['Ссылка']}\n"
            "──────────────────"
        )
        await bot.send_message(chat_id=chat_id, text=message, reply_markup=like_dislike_keyboard)
        logger.info(f"Новость {news_index} отправлена пользователю {chat_id}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

# Обработка нажатий на "👍" и "👎"
async def handle_like_dislike(callback: types.CallbackQuery, reaction: str):
    # Извлекаем индекс новости из callback_data
    news_index = int(callback.data.split("_")[1])

    # Получаем заголовок новости
    news_title = df.iloc[news_index]['Заголовок']

    # Отправляем пользователю сообщение о его реакции
    if reaction == "like":
        await callback.message.answer(f"Вы поставили 👍 на новость: {news_title}")
    elif reaction == "dislike":
        await callback.message.answer(f"Вы поставили 👎 на новость: {news_title}")

    # Отправляем следующую новость
    next_news_index = news_index + 1
    if next_news_index < len(df):
        await send_news_to_telegram(callback.message.chat.id, callback.bot, next_news_index)
    else:
        await callback.message.answer("Новости закончились.")

    # Подтверждаем обработку callback-запроса
    await callback.answer()
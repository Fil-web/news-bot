from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from database.database import add_reaction, create_connection, create_table
from news.service import news_store
from utils.logger import logger

command_router = Router()
callback_router = Router()
text_router = Router()

conn = create_connection("database/reactions.db")
if conn is not None:
    create_table(conn)

inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📰 Новости", callback_data="news"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
        ],
    ]
)

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📰 Новости"),
            KeyboardButton(text="📊 Статистика"),
        ],
        [
            KeyboardButton(text="ℹ️ Помощь"),
        ],
    ],
    resize_keyboard=True,
)


async def build_stats_message() -> str:
    total = await news_store.total_news()
    last_updated = await news_store.get_last_updated()
    if last_updated is None:
        return f"Всего новостей: {total}\nОбновление еще не выполнялось."

    updated_text = last_updated.astimezone().strftime("%d.%m.%Y %H:%M:%S %Z")
    return f"Всего новостей: {total}\nПоследнее обновление: {updated_text}"


@command_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=reply_keyboard)


@callback_router.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    if data == "news":
        await send_news_to_telegram(callback.message.chat.id, callback.bot, 0)
    elif data == "stats":
        await callback.message.answer(await build_stats_message())
    elif data == "help":
        await callback.message.answer(
            "Используйте кнопки для навигации. "
            "📰 Новости покажут свежие записи из zab.ru, "
            "📊 Статистика покажет количество новостей и время последнего обновления."
        )
    elif data.startswith("like_"):
        await handle_like_dislike(callback, "like")
    elif data.startswith("dislike_"):
        await handle_like_dislike(callback, "dislike")
    await callback.answer()


@text_router.message()
async def handle_text(message: types.Message):
    text = message.text
    if text == "📰 Новости":
        await send_news_to_telegram(message.chat.id, message.bot, 0)
    elif text == "📊 Статистика":
        await message.answer(await build_stats_message())
    elif text == "ℹ️ Помощь":
        await message.answer(
            "Используйте кнопки для навигации. "
            "📰 Новости покажут свежие записи из zab.ru, "
            "📊 Статистика покажет количество новостей и время последнего обновления."
        )


async def send_news_to_telegram(chat_id: int, bot, news_index: int):
    try:
        row = await news_store.get_news_item(news_index)
        if row is None:
            await bot.send_message(chat_id=chat_id, text="Новости закончились.")
            return

        like_dislike_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="👍", callback_data=f"like_{news_index}"),
                    InlineKeyboardButton(text="👎", callback_data=f"dislike_{news_index}"),
                ]
            ]
        )

        message = (
            f"📰 <b>Заголовок:</b> {row.get('Заголовок', 'Нет данных')}\n"
            f"📅 <b>Дата:</b> {row.get('Дата', 'Нет данных')}\n"
            f"📝 <b>Описание:</b> {row.get('Описание', 'Нет данных')}\n"
            f"🔗 <b>Ссылка:</b> {row.get('Ссылка', 'Нет данных')}\n"
            "──────────────────"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=like_dislike_keyboard,
            disable_web_page_preview=True,
        )
        logger.info("Новость %s отправлена пользователю %s.", news_index, chat_id)
    except Exception as exc:
        logger.error("Ошибка при отправке сообщения: %s", exc)
        await bot.send_message(chat_id=chat_id, text="Не удалось отправить новость.")


async def handle_like_dislike(callback: types.CallbackQuery, reaction: str):
    news_index = int(callback.data.split("_")[1])
    row = await news_store.get_news_item(news_index)
    if row is None:
        await callback.message.answer("Новость уже недоступна, попробуйте открыть список заново.")
        return

    if conn is not None and callback.from_user is not None:
        add_reaction(conn, callback.from_user.id, news_index, reaction)

    news_title = row.get("Заголовок", "Без названия")

    if reaction == "like":
        await callback.message.answer(f"Вы поставили 👍 на новость: {news_title}")
    elif reaction == "dislike":
        await callback.message.answer(f"Вы поставили 👎 на новость: {news_title}")

    next_news_index = news_index + 1
    total = await news_store.total_news()
    if next_news_index < total:
        await send_news_to_telegram(callback.message.chat.id, callback.bot, next_news_index)
    else:
        await callback.message.answer("Новости закончились.")

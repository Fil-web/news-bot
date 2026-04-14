from __future__ import annotations

import sqlite3
from pathlib import Path
from sqlite3 import Error

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database" / "reactions.db"


def create_connection(db_file: str | Path | None = None):
    target = Path(db_file) if db_file else DATABASE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(target)
        print(f"Подключение к SQLite успешно: {target}")
        return conn
    except Error as exc:
        print(f"Ошибка подключения к SQLite: {exc}")
    return conn


def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                news_index INTEGER NOT NULL,
                reaction TEXT NOT NULL,
                UNIQUE(user_id, news_index)
            )
            '''
        )
        conn.commit()
        print("Таблица reactions создана или уже существует.")
    except Error as exc:
        print(f"Ошибка при создании таблицы: {exc}")


def add_reaction(conn, user_id, news_index, reaction):
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT OR REPLACE INTO reactions (user_id, news_index, reaction)
            VALUES (?, ?, ?)
            ''',
            (user_id, news_index, reaction),
        )
        conn.commit()
        print(f"Реакция {reaction} для новости {news_index} пользователя {user_id} сохранена.")
    except Error as exc:
        print(f"Ошибка при добавлении реакции: {exc}")


def get_reaction(conn, user_id, news_index):
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT reaction FROM reactions
            WHERE user_id = ? AND news_index = ?
            ''',
            (user_id, news_index),
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as exc:
        print(f"Ошибка при получении реакции: {exc}")
        return None

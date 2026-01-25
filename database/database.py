import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Подключение к SQLite успешно: {db_file}")
        return conn
    except Error as e:
        print(f"Ошибка подключения к SQLite: {e}")
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                news_index INTEGER NOT NULL,
                reaction TEXT NOT NULL,
                UNIQUE(user_id, news_index)
            )
        ''')
        conn.commit()
        print("Таблица reactions создана или уже существует.")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")

def add_reaction(conn, user_id, news_index, reaction):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO reactions (user_id, news_index, reaction)
            VALUES (?, ?, ?)
        ''', (user_id, news_index, reaction))
        conn.commit()
        print(f"Реакция {reaction} для новости {news_index} пользователя {user_id} сохранена.")
    except Error as e:
        print(f"Ошибка при добавлении реакции: {e}")

def get_reaction(conn, user_id, news_index):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT reaction FROM reactions
            WHERE user_id = ? AND news_index = ?
        ''', (user_id, news_index))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Ошибка при получении реакции: {e}")
        return None
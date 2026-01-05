import sqlite3
import os

DB_DIR = "/app/db"
DB_NAME = f"{DB_DIR}/users.sqlite"

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            born_date TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            nickname TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(name: str, last_name: str, born_date: str, email: str, nickname: str, password_hash: str) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, last_name, born_date, email, nickname, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
            (name, last_name, born_date, email, nickname, password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_user_by_nickname(nickname: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, password_hash, email, born_date FROM users WHERE nickname=?", (nickname,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_password(nickname: str, new_password_hash: str) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash=? WHERE nickname=?", (new_password_hash, nickname))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except:
        return False

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = Path(os.getenv("DATABASE_PATH"))


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)  # Creates file if it doesn't exist
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT CHECK(role IN ('sysadmin', 'user')) DEFAULT 'user',
                email TEXT UNIQUE NOT NULL,
                google_id TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                salutation TEXT DEFAULT 'Dr.',
                license_number TEXT DEFAULT NULL
            )
        """
        )
        conn.commit()
    finally:
        conn.close()


def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

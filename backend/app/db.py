import os

import psycopg2
from dotenv import load_dotenv

# import sqlite3
# from pathlib import Path


load_dotenv()
# DATABASE_PATH = Path(os.getenv("DATABASE_PATH")).resolve()
DATABASE_PATH = os.getenv("DATABASE_PATH")
if not DATABASE_PATH:
    raise ValueError("DATABASE_PATH is not set")
print(f"DATABASE_PATH: {DATABASE_PATH}")
# print(f"database exists: {DATABASE_PATH.exists()}")


def init_db():
    # conn = sqlite3.connect(DATABASE_PATH)  # Creates file if it doesn't exist
    conn = psycopg2.connect(DATABASE_PATH)
    try:
        cursor = conn.cursor()

        create_table_commands = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'user' CHECK(role IN ('sysadmin', 'user')),
                email TEXT UNIQUE NOT NULL,
                google_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                salutation TEXT DEFAULT 'Dr.',
                license_number TEXT
            );
            """
        ]
        for command in create_table_commands:
            cursor.execute(command)
        conn.commit()
    finally:
        conn.close()


def get_db_connection():
    # return sqlite3.connect(DATABASE_PATH)
    return psycopg2.connect(DATABASE_PATH)

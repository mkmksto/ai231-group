import os
from typing import Any, Dict, Generator, List, Optional

import psycopg2
from dotenv import load_dotenv

# from psycopg2 import sql
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_PATH")
if not DATABASE_URL:
    raise ValueError("DATABASE_PATH is not set")

# Mask the password in the database URL before printing
masked_url = DATABASE_URL
if "://" in DATABASE_URL and "@" in DATABASE_URL:
    prefix, rest = DATABASE_URL.split("://", 1)
    creds, host = rest.split("@", 1)
    if ":" in creds:
        user, pwd = creds.split(":", 1)
        masked_url = f"{prefix}://{user}:****@{host}"
print(f"DATABASE_PATH: {masked_url}")


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Create tables if they do not exist."""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            role VARCHAR DEFAULT 'user' CHECK (role IN ('sysadmin', 'user')),
            email VARCHAR UNIQUE NOT NULL,
            google_id VARCHAR UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            salutation VARCHAR DEFAULT 'Dr.',
            license_number VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS models (
            model_id VARCHAR PRIMARY KEY,
            s3_link VARCHAR NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            F1 INTEGER,
            Recall INTEGER,
            Precision INTEGER,
            Accuracy INTEGER
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS images (
            image_id VARCHAR PRIMARY KEY,
            s3_link VARCHAR NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            update_date TIMESTAMP,
            label VARCHAR,
            img_type VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS training_runs (
            training_id VARCHAR PRIMARY KEY,
            training_start TIMESTAMP NOT NULL,
            training_time INTEGER,
            model_id VARCHAR,
            status VARCHAR,
            initial_hyperparams VARCHAR,
            pretrained_model_used VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS training_run_training_images (
            id SERIAL PRIMARY KEY,
            training_id VARCHAR REFERENCES training_runs(training_id),
            image_id VARCHAR REFERENCES images(image_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS training_run_validation_images (
            id SERIAL PRIMARY KEY,
            training_id VARCHAR REFERENCES training_runs(training_id),
            image_id VARCHAR REFERENCES images(image_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS training_run_testing_images (
            id SERIAL PRIMARY KEY,
            training_id VARCHAR REFERENCES training_runs(training_id),
            image_id VARCHAR REFERENCES images(image_id)
        );
        """,
    ]
    with get_conn() as conn:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()


# --- CRUD Functions ---
# Users
def add_user(
    name: str,
    email: str,
    google_id: str,
    role: str = "user",
    salutation: str = "Dr.",
    license_number: Optional[str] = None,
):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO users (name, email, google_id, role, salutation, license_number) VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id""",
                (name, email, google_id, role, salutation, license_number),
            )
            row = cur.fetchone()
            # user_id = row.get("user_id") if row else None
        conn.commit()
    # return user_id
    return row


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None


# Models
def add_model(
    model_id: str,
    s3_link: str,
    upload_date,
    F1: Optional[int] = None,
    Recall: Optional[int] = None,
    Precision: Optional[int] = None,
    Accuracy: Optional[int] = None,
) -> Optional[str]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO models (model_id, s3_link, upload_date, F1, Recall, Precision, Accuracy) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING model_id""",
                (model_id, s3_link, upload_date, F1, Recall, Precision, Accuracy),
            )
            row = cur.fetchone()
            mid = row.get("model_id") if row else None
        conn.commit()
    return mid


def get_model(model_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM models WHERE model_id = %s", (model_id,))
            row = cur.fetchone()
            return dict(row) if row else None


# Images
def add_image(
    image_id: str,
    s3_link: str,
    upload_date,
    update_date=None,
    label: Optional[str] = None,
    img_type: Optional[str] = None,
) -> Optional[str]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO images (image_id, s3_link, upload_date, update_date, label, img_type) VALUES (%s, %s, %s, %s, %s, %s) RETURNING image_id""",
                (image_id, s3_link, upload_date, update_date, label, img_type),
            )
            row = cur.fetchone()
            iid = row.get("image_id") if row else None
        conn.commit()
    return iid


def get_image(image_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM images WHERE image_id = %s", (image_id,))
            row = cur.fetchone()
            return dict(row) if row else None


# Training Runs
def add_training_run(
    training_id: str,
    training_start,
    training_time: Optional[int] = None,
    model_id: Optional[str] = None,
    status: Optional[str] = None,
    initial_hyperparams: Optional[str] = None,
    pretrained_model_used: Optional[str] = None,
) -> Optional[str]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO training_runs (training_id, training_start, training_time, model_id, status, initial_hyperparams, pretrained_model_used) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING training_id""",
                (
                    training_id,
                    training_start,
                    training_time,
                    model_id,
                    status,
                    initial_hyperparams,
                    pretrained_model_used,
                ),
            )
            row = cur.fetchone()
            tid = row.get("training_id") if row else None
        conn.commit()
    return tid


def get_training_run(training_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM training_runs WHERE training_id = %s", (training_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None


# Junction tables (example for training images)
def add_training_run_training_image(training_id: str, image_id: str) -> Optional[int]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO training_run_training_images (training_id, image_id) VALUES (%s, %s) RETURNING id""",
                (training_id, image_id),
            )
            row = cur.fetchone()
            jid = row.get("id") if row else None
        conn.commit()
    return jid


def get_training_images(training_id: str) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM training_run_training_images WHERE training_id = %s",
                (training_id,),
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows] if rows else []


# # Similar functions can be written for validation and testing images as needed.

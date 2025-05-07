import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# import sqlite3
# from pathlib import Path


load_dotenv()
# DATABASE_PATH = Path(os.getenv("DATABASE_PATH")).resolve()
DATABASE_URL = os.getenv("DATABASE_PATH")
if not DATABASE_URL:
    raise ValueError("DATABASE_PATH is not set")
print(f"DATABASE_PATH: {DATABASE_URL}")
# print(f"database exists: {DATABASE_PATH.exists()}")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define User model
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, default="user")
    email = Column(String, unique=True, nullable=False)
    google_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    salutation = Column(String, default="Dr.")
    license_number = Column(String)

    __table_args__ = (
        CheckConstraint(role.in_(["sysadmin", "user"]), name="role_check"),
    )


def init_db():
    # conn = sqlite3.connect(DATABASE_PATH)  # Creates file if it doesn't exist
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

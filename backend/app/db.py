import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_PATH")
if not DATABASE_URL:
    raise ValueError("DATABASE_PATH is not set")
print(f"DATABASE_PATH: {DATABASE_URL}")

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
    created_at = Column(DateTime, server_default=func.now())
    salutation = Column(String, default="Dr.")
    license_number = Column(String)

    __table_args__ = (
        CheckConstraint(role.in_(["sysadmin", "user"]), name="role_check"),
    )


# Define Model model
class Model(Base):
    __tablename__ = "models"

    model_id = Column(String, primary_key=True, index=True)  # uuid as str
    s3_link = Column(String, nullable=False)
    upload_date = Column(DateTime, nullable=False)
    F1 = Column(Integer)
    Recall = Column(Integer)
    Precision = Column(Integer)
    Accuracy = Column(Integer)


# Define Image model
class ImageTable(Base):
    __tablename__ = "images"

    image_id = Column(String, primary_key=True, index=True)  # uuid as str
    s3_link = Column(String, nullable=False)
    upload_date = Column(DateTime, nullable=False)
    update_date = Column(DateTime)
    label = Column(String)  # label_enum (nullable) (glioma, etc)
    img_type = Column(String)  # image_type_enum (nullable) (original or feedback)


# Define TrainingRun model
class TrainingRun(Base):
    __tablename__ = "training_runs"

    training_id = Column(String, primary_key=True, index=True)  # uuid as str
    training_start = Column(DateTime, nullable=False)
    training_time = Column(Integer)
    model_id = Column(String, nullable=True)  # ForeignKey can be added if needed
    status = Column(String)  # success / fail
    initial_hyperparams = Column(String)  # JSON as str (nullable/optional)
    pretrained_model_used = Column(String)
    # ... other specs as needed


# Junction tables for training_run <-> images (for training, validation, testing datasets)
class TrainingRunTrainingImage(Base):
    __tablename__ = "training_run_training_images"
    id = Column(Integer, primary_key=True)
    training_id = Column(String, ForeignKey("training_runs.training_id"))
    image_id = Column(String, ForeignKey("images.image_id"))


class TrainingRunValidationImage(Base):
    __tablename__ = "training_run_validation_images"
    id = Column(Integer, primary_key=True)
    training_id = Column(String, ForeignKey("training_runs.training_id"))
    image_id = Column(String, ForeignKey("images.image_id"))


class TrainingRunTestingImage(Base):
    __tablename__ = "training_run_testing_images"
    id = Column(Integer, primary_key=True)
    training_id = Column(String, ForeignKey("training_runs.training_id"))
    image_id = Column(String, ForeignKey("images.image_id"))


def init_db():
    # conn = sqlite3.connect(DATABASE_PATH)  # Creates file if it doesn't exist
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

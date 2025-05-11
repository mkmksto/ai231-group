from datetime import datetime, timedelta
from os import getenv
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import User, get_db

load_dotenv()

ACCESS_TOKEN_SECRET = getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = getenv("REFRESH_TOKEN_SECRET")
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 0.2 # dev
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 7

if ACCESS_TOKEN_SECRET is None:
    raise ValueError("ACCESS_TOKEN_SECRET is not set")

if REFRESH_TOKEN_SECRET is None:
    raise ValueError("REFRESH_TOKEN_SECRET is not set")


# Validation Schemas
class TokenOrDbUserPayload(BaseModel):
    user_id: int
    name: str
    role: str
    email: str
    google_id: str


class RawAccessTokenCookie(BaseModel):
    access_token: str


class RawRefreshTokenCookie(BaseModel):
    refresh_token: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)


def get_at_payload(token: str):
    print("...inside get_at_payload")
    invalid_at_response = {
        "is_at_valid": False,
        "is_at_expired": True,
        "payload": None,
    }

    if not token:
        return invalid_at_response

    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
        if not payload:
            return invalid_at_response

        exp = payload.get("exp")
        if exp is None:
            return invalid_at_response

        return {
            "is_at_valid": True,
            "is_at_expired": exp < datetime.utcnow().timestamp(),
            "payload": payload,
        }
    except JWTError:
        return invalid_at_response


def get_rt_payload(token: str):
    invalid_rt_response = {
        "is_rt_valid": False,
        "is_rt_expired": True,
        "payload": None,
    }

    if not token:
        return invalid_rt_response

    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM])
        if not payload:
            return invalid_rt_response

        exp = payload.get("exp")
        if exp is None:
            return invalid_rt_response

        return {
            "is_rt_valid": True,
            "is_rt_expired": exp < datetime.utcnow().timestamp(),
            "payload": payload,
        }
    except JWTError:
        return invalid_rt_response


def refresh_at_token(refresh_token: str, db: Session = next(get_db())):
    print("...inside refresh_at_token")
    is_rt_valid, is_rt_expired, payload = get_rt_payload(refresh_token).values()
    print(
        {
            "is_rt_valid": is_rt_valid,
            "is_rt_expired": is_rt_expired,
            # "payload": payload,
        }
    )
    rt_payload = payload
    if not is_rt_valid or is_rt_expired or not rt_payload:
        raise JWTError("Invalid refresh token")

    db_user = db.query(User).filter(User.user_id == rt_payload.get("user_id")).first()
    if not db_user:
        raise JWTError("User not found")

    user = {
        "user_id": db_user.user_id,
        "name": db_user.name,
        "role": db_user.role,
        "email": db_user.email,
        "google_id": db_user.google_id,
    }

    return create_access_token(user)

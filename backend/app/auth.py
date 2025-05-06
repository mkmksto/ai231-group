from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
from jose import jwt

load_dotenv()

ACCESS_TOKEN_SECRET = getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = getenv("REFRESH_TOKEN_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: timedelta = None):
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

        return {
            "is_at_valid": True,
            "is_at_expired": payload.get("exp") < datetime.utcnow().timestamp(),
            "payload": payload,
        }
    except jwt.JWTError:
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

        return {
            "is_rt_valid": True,
            "is_rt_expired": payload.get("exp") < datetime.utcnow().timestamp(),
            "payload": payload,
        }
    except jwt.JWTError:
        return invalid_rt_response

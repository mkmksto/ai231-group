import os

from dotenv import load_dotenv
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import (
    RawAccessTokenCookie,
    RawRefreshTokenCookie,
    get_at_payload,
    get_rt_payload,
    refresh_at_token,
)

load_dotenv()
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")


# Custom middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(">>>> inside auth middleware ---------------------------- ")
        allowed_paths = ["/api/auth", "/assets", "/health"]

        # Check if the request path starts with any of the allowed paths
        if (
            any(request.url.path.startswith(path) for path in allowed_paths)
            or request.url.path == "/"
        ):
            print("...inside auth middleware: allowed endpoint, skipping auth check")
            return await call_next(request)

        _access_token = request.cookies.get("access_token") or ""
        _refresh_token = request.cookies.get("refresh_token") or ""
        access_token, refresh_token = {"access_token": "", "refresh_token": ""}
        access_token = RawAccessTokenCookie(access_token=_access_token)
        try:
            refresh_token = RawRefreshTokenCookie(refresh_token=_refresh_token)
        except ValidationError as e:
            print("RT might be empty or expired")
            # return RedirectResponse(url=FRONTEND_BASE_URL, status_code=302)
            raise HTTPException(status_code=401, detail=str(e))
        print("both at and rt are strings")
        print("access token: ")
        print(access_token)

        at_payload: dict = get_at_payload(access_token.access_token)
        rt_payload: dict = get_rt_payload(refresh_token.refresh_token)
        is_at_valid, is_at_expired, at_payload = at_payload.values()
        is_rt_valid, is_rt_expired, rt_payload = rt_payload.values()
        print(
            {
                "is_at_valid": is_at_valid,
                "is_at_expired": is_at_expired,
                "is_rt_valid": is_rt_valid,
            }
        )

        if is_rt_valid:
            print(">>> middleware: rt is valid")
            if is_at_valid and at_payload:
                print("valid at and rt")
                user = at_payload
                request.state.user = user
                response = await call_next(request)
                return response
            if not access_token or is_at_expired:
                print("at is expired but rt is valid")
                new_at = refresh_at_token(refresh_token.refresh_token)
                _, _, new_at_payload = get_at_payload(new_at).values()
                user = new_at_payload
                request.state.user = user
                response = await call_next(request)
                return response
        else:
            print("rt is invalid")
            # Get the origin from the request headers
            # return RedirectResponse(url=FRONTEND_BASE_URL, status_code=302)
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            # response = await call_next(request)
            # return response

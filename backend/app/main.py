import os
import random
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    get_at_payload,
    get_rt_payload,
)
from app.db import get_db_connection, init_db
from app.utils import BACKEND_DIST_PATH
from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from PIL import Image

# ML Imports
# from numpy import ndarray
# import torch
# import torch.nn.functional as F
# from training.inference_engine.tensor_rt_inference import BrainTumorClassifier

#
# ----
#

root_dir = Path(__file__).parent.parent.parent
print("root_dir: ", root_dir)
sample_test_image = "training/brain_tumor_dataset/Testing/glioma_tumor/image(1).jpg"
image_path = Path(root_dir / sample_test_image)
image = Image.open(image_path).convert("RGB")

# OS-specific engine paths
linux_engine = "training/inference_engine/brain_tumor_linux.engine"
windows_engine = "training/inference_engine/brain_tumor.engine"

# Select engine based on OS
engine_path = windows_engine
if sys.platform.startswith("linux"):
    engine_path = linux_engine
elif sys.platform.startswith("win"):
    engine_path = windows_engine
else:
    print("Unsupported operating system. Only Linux and Windows are supported.")
    # raise OSError("Unsupported operating system. Only Linux and Windows are supported.")

model_location = Path(root_dir / engine_path)
print(f"Using engine: {model_location}")
print(model_location.exists())
print(model_location.absolute())

# model = BrainTumorClassifier(model_location)

load_dotenv()

#
# FastAPI app
#

IS_VERCEL = os.getenv("IS_VERCEL")
CALLBACK_URL = os.getenv("CALLBACK_URL")
print("loaded environment variables: ")
print(
    {
        "IS_VERCEL": IS_VERCEL,
        "CALLBACK_URL": CALLBACK_URL,
    }
)

# -----
# OAuth
# -----

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")


app = FastAPI(
    title="Medical Image Classification API",
    description="API for brain tumor image classification",
    version="1.0.0",
)

init_db()


app.mount(
    "/assets",
    StaticFiles(directory=str((BACKEND_DIST_PATH / "assets").resolve())),
    name="assets",
)


# Auth endpoints
@app.get("/api/auth/google/login")
async def login():
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"
    )


@app.post("/api/auth/logout")
async def logout():
    # TODO: clear cookies
    return {"message": "Logged out"}


@app.get("/api/auth/google/callback")
async def callback(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    google_res = requests.post(token_url, data=data, timeout=10)
    access_token = google_res.json().get("access_token")
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    user_data = user_info.json()

    # Find or create user
    print("finding or creating user")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Find or create user
        cursor.execute("SELECT * FROM users WHERE google_id = ?", (user_data["id"],))
        user = cursor.fetchone()

        # Create user if they don't exist
        if not user:
            print("no existing user found, creating new user")
            cursor.execute(
                """
                INSERT INTO users (name, email, google_id, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_data["name"],
                    user_data["email"],
                    user_data["id"],
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

            cursor.execute(
                "SELECT * FROM users WHERE google_id = ?", (user_data["id"],)
            )
            user = cursor.fetchone()

        # Convert user tuple to dict
        user_dict = {
            "user_id": user[0],
            "name": user[1],
            "role": user[2],
            "email": user[3],
            "google_id": user[4],
        }

        # create access and refresh tokens with user claims
        access_token = create_access_token(user_dict)
        refresh_token = create_refresh_token(user_dict)

        # set the access tokens to the cookies (HTTP only)
        response = RedirectResponse(FRONTEND_BASE_URL)
        response.set_cookie(
            key="access_token",
            samesite="lax",
            value=access_token,
            path="/",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            samesite="lax",
            value=refresh_token,
            path="/",
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Auth Error / Error in creating user: {str(e)}"},
        )

    # do not edit anything below this line
    finally:
        conn.close()

    return response
    # return RedirectResponse(FRONTEND_BASE_URL)


@app.get("/api/auth/me")
async def me(request: Request):
    # get the user from the cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    at_payload: dict = get_at_payload(access_token)
    rt_payload: dict = get_rt_payload(refresh_token)
    is_at_valid, is_at_expired, at_payload = at_payload.values()
    is_rt_valid, is_rt_expired, rt_payload = rt_payload.values()
    print(
        {
            "is_at_valid": is_at_valid,
            "is_at_expired": is_at_expired,
            "is_rt_valid": is_rt_valid,
        }
    )

    # TODO: implement refresh token logic using fastapi middleware

    # Get user from db after validating access token
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE google_id = ?", (at_payload["google_id"],)
    )
    user = cursor.fetchone()
    conn.close()

    # if is_rt_valid:
    #     print('context: inside auth middleware: refresh token is valid')
    #     if is_at_valid and at_payload:
    #         print('valid access token and refresh token')

    # see app/db.py for the user table schema
    return user


@app.post("/api/predict")
async def predict_tumor_class(
    file: UploadFile = File(...),
):
    try:

        contents = await file.read()
        image_from_frontend = Image.open(BytesIO(contents)).convert("RGB")

        class_mapping = {
            0: "glioma_tumor",
            1: "meningioma_tumor",
            2: "no_tumor",
            3: "pituitary_tumor",
        }
        print(class_mapping)

        predicted_class = random.choice(list(class_mapping.values()))
        confidence = random.random()

        return JSONResponse(
            {
                "prediction": predicted_class,
                "confidence": confidence,  # Actual confidence score from model
            }
        )

        # # uncomment when using the actual model
        # output: ndarray = model.inference(image_from_frontend)
        # print("output: ", output)
        # print("output dimensions: ", output.shape)

        # # Apply softmax to get probabilities
        # probabilities = torch.nn.functional.softmax(torch.from_numpy(output), dim=1)
        # confidence = probabilities.max().item()
        # print("confidence: ", confidence)

        # predicted_class_number = output.argmax().item()
        # print(predicted_class_number)  # Output: 1

        # # Mapping to label (optional):
        # class_mapping = {
        #     0: "glioma_tumor",
        #     1: "meningioma_tumor",
        #     2: "no_tumor",
        #     3: "pituitary_tumor",
        # }

        # predicted_class = class_mapping[predicted_class_number]
        # print("predicted_class", predicted_class)

        # return JSONResponse(
        #     {
        #         "prediction": predicted_class,
        #         "confidence": confidence,  # Actual confidence score from model
        #     }
        # )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"Error processing image: {str(e)}"}
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


app.mount(
    "/",
    StaticFiles(directory=str(BACKEND_DIST_PATH), html=True),
    name="backend",
)

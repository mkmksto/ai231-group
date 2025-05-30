import os
import random
import sys
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from PIL import Image
from sqlalchemy.orm import Session

from .auth import TokenOrDbUserPayload
from .db import ImageTable
from .models import FeedbackInput
from .storage import BUCKET_NAME, update_blob_metadata, upload_to_gcs

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests

from .auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
)
from .db import User, get_db, init_db
from .middleware import AuthMiddleware
from .utils import BACKEND_DIST_PATH

# ML Imports
# from numpy import ndarray
# import torch
# import torch.nn.functional as F
# from training.inference_engine.tensor_rt_inference import BrainTumorClassifier

# For ML inference (uncomment when using the actual model)
root_dir = Path(__file__).parent.parent.parent
# print("root_dir: ", root_dir)
# sample_test_image = "training/brain_tumor_dataset/Testing/glioma_tumor/image(1).jpg"
# image_path = Path(root_dir / sample_test_image)
# image = Image.open(image_path).convert("RGB")

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
    # print("Unsupported operating system. Only Linux and Windows are supported.")
    pass
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
GOOGLE_COMPUTE_ENDPOINT = os.getenv("GOOGLE_COMPUTE_ENDPOINT")
if any(
    [
        GOOGLE_CLIENT_ID is None,
        GOOGLE_CLIENT_SECRET is None,
        GOOGLE_REDIRECT_URI is None,
        FRONTEND_BASE_URL is None,
        GOOGLE_COMPUTE_ENDPOINT is None,
    ]
):
    raise ValueError("Missing environment variables")

app = FastAPI(
    title="Medical Image Classification API",
    description="API for brain tumor image classification",
    version="1.0.0",
)

init_db()

app.add_middleware(AuthMiddleware)
# Add CORS middleware for frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount(
#     "/assets",
#     StaticFiles(directory=str((BACKEND_DIST_PATH / "assets").resolve())),
#     name="assets",
# )


# Auth endpoints
@app.get("/api/auth/google/login")
async def login():
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"
    )


@app.post("/api/auth/logout")
async def logout():
    response = JSONResponse(
        content={
            "success": True,
            "redirect": f"{FRONTEND_BASE_URL}",
            "message": "Logged out successfully",
        }
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@app.get("/api/auth/google/callback")
async def callback(code: str, db: Session = Depends(get_db)):
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
    try:
        # Find or create user
        print("finding user")
        user = db.query(User).filter(User.google_id == user_data["id"]).first()
        print("user: ", user)

        # Create user if they don't exist
        if not user:
            print("no existing user found, creating new user")
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                google_id=user_data["id"],
                created_at=datetime.now(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Convert user to dict
        user_dict = {
            "user_id": user.user_id,
            "name": user.name,
            "role": user.role,
            "email": user.email,
            "google_id": user.google_id,
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

    return response


@app.get("/api/me")
async def me(request: Request, db: Session = Depends(get_db)):
    print(">> .... inside /api/me")
    _user = request.state.user
    print("_user id: ", _user["user_id"])
    user = TokenOrDbUserPayload(**_user)

    # Get user from db after validating access token
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if not db_user:
        return JSONResponse(
            status_code=404,
            content={"message": "User not found"},
        )

    return {
        "user_id": db_user.user_id,
        "name": db_user.name,
        "role": db_user.role,
        "email": db_user.email,
        "google_id": db_user.google_id,
    }


@app.post("/api/feedback")
async def feedback(
    feedback_input: FeedbackInput,
    db: Session = Depends(get_db),
):
    print("inside /api/feedback")
    print("image_id: ", feedback_input.image_id)
    print("label: ", feedback_input.label)
    try:
        image = (
            db.query(ImageTable)
            .filter(ImageTable.image_id == feedback_input.image_id)
            .first()
        )
        if not image:
            return JSONResponse(status_code=404, content={"message": "Image not found"})

        # Update database
        setattr(image, "label", feedback_input.label)
        setattr(image, "update_date", datetime.now())
        db.commit()
        db.refresh(image)

        # Update GCS metadata
        # Extract blob name from GCS path (remove gs://bucket-name/ prefix)
        gcs_path = str(image.s3_link)
        print("gcs_path: ", gcs_path)
        if gcs_path.startswith(f"gs://{BUCKET_NAME}/"):
            blob_name = gcs_path[len(f"gs://{BUCKET_NAME}/") :]
            print("blob_name: ", blob_name)
            update_blob_metadata(
                blob_name,
                {
                    "true_label": feedback_input.label,
                    "last_updated": datetime.now().isoformat(),
                },
            )

        return {
            "success": True,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"Error processing image: {str(e)}"}
        )


@app.post("/api/predict")
async def predict_tumor_class(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    print("---- inside /api/predict")
    try:
        contents = await file.read()
        image_from_frontend = Image.open(BytesIO(contents)).convert("RGB")
        # Save the image temporarily
        temp_path = f"/tmp/{file.filename}"
        image_from_frontend.save(temp_path)

        destination_blob_name = (
            f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        )
        gcs_path = upload_to_gcs(
            source_file_path=temp_path,
            destination_blob_name=destination_blob_name,
        )
        new_image = ImageTable(
            image_id=str(uuid.uuid4()),
            s3_link=gcs_path,
            upload_date=datetime.now(),
            update_date=datetime.now(),
            label="",
            img_type="feedback",
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        # print("new_image id: ", new_image.image_id)

        # class_mapping = {
        #     0: "glioma_tumor",
        #     1: "meningioma_tumor",
        #     2: "no_tumor",
        #     3: "pituitary_tumor",
        # }
        # endpoint = f"{GOOGLE_COMPUTE_ENDPOINT}"
        print("before predict service")
        # endpoint = "http://localhost:8001/predict/gcs"
        endpoint = "http://compute_engine:8001/predict/gcs"
        response = requests.post(
            endpoint,
            json={"uri": new_image.s3_link},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        print("response: ", response)
        print("after predict service")
        response_json = response.json()
        predicted_class = response_json.get("predicted_class", "prediction failed")
        confidence = response_json.get("confidence", 0.0)

        # predicted_class = random.choice(list(class_mapping.values()))
        # confidence = random.uniform(0.7, 0.98)

        return JSONResponse(
            {
                "prediction": predicted_class,
                "confidence": confidence,  # Actual confidence score from model
                "image_id": new_image.image_id,
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


# app.mount(
#     "/",
#     StaticFiles(directory=str(BACKEND_DIST_PATH), html=True),
#     name="backend",
# )

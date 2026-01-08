import os
import sys
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, File, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer

# from fastapi.staticfiles import StaticFiles
from PIL import Image

from .auth import TokenOrDbUserPayload
from .db import (
    add_image,
    add_user,
    get_conn,
    get_image,
    get_user_by_email,
    get_user_by_id,
    init_db,
)
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
from .middleware import AuthMiddleware

# from .utils import BACKEND_DIST_PATH

# For ML inference (uncomment when using the actual model)
root_dir = Path(__file__).parent.parent.parent

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
    print("finding user")
    user = get_user_by_email(user_data["email"])
    print("user: ", user)
    if not user:
        print("no existing user found, creating new user")
        user = add_user(
            name=user_data["name"], email=user_data["email"], google_id=user_data["id"]
        )
        # user: Dict = get_user_by_email(user_data["email"])
    print("user: ", user)
    user_dict = {
        "user_id": user["user_id"],
        "name": user["name"],
        "role": user["role"],
        "email": user["email"],
        "google_id": user["google_id"],
    }

    # create access and refresh tokens with user claims
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_dict)

    # set the access tokens to the cookies (HTTP only)
    response = RedirectResponse(FRONTEND_BASE_URL or "")
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

    return response


@app.get("/api/me")
async def me(request: Request):
    print(">> .... inside /api/me")
    _user = request.state.user
    print("_user id: ", _user["user_id"])
    user = TokenOrDbUserPayload(**_user)

    # Get user from db after validating access token
    db_user = get_user_by_id(user.user_id)
    if not db_user:
        return JSONResponse(
            status_code=404,
            content={"message": "User not found"},
        )

    return {
        "user_id": db_user["user_id"],
        "name": db_user["name"],
        "role": db_user["role"],
        "email": db_user["email"],
        "google_id": db_user["google_id"],
    }


@app.post("/api/feedback")
async def feedback(
    feedback_input: FeedbackInput,
):
    print("inside /api/feedback")
    print("image_id: ", feedback_input.image_id)
    print("label: ", feedback_input.label)
    try:
        image = get_image(feedback_input.image_id)
        if not image:
            return JSONResponse(status_code=404, content={"message": "Image not found"})

        # Update database
        # from psycopg2 import sql

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE images SET label = %s, update_date = %s WHERE image_id = %s""",
                    (feedback_input.label, datetime.now(), feedback_input.image_id),
                )
            conn.commit()
        image = get_image(feedback_input.image_id)
        if not image:
            return JSONResponse(status_code=404, content={"message": "Image not found"})

        # Update GCS metadata
        # Extract blob name from GCS path (remove gs://bucket-name/ prefix)
        gcs_path = str(image["s3_link"])
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
    file: UploadFile = File(...),
    sample: bool = Query(False, description="Enable sample mode to return dummy data"),
):
    print("---- inside /api/predict")
    print(f"Sample mode: {sample}")

    # If sample mode is enabled, return dummy data
    if sample:
        import random

        # Hardcoded class - change this to whatever class you want to return
        DUMMY_CLASS = "glioma_tumor"  # Options: "glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"
        # Random confidence between 80-100 (0.80-1.00)
        dummy_confidence = random.uniform(0.80, 1.00)

        # Still save the image to database for consistency
        contents = await file.read()
        image_from_frontend = Image.open(BytesIO(contents)).convert("RGB")
        temp_path = f"/tmp/{file.filename}"
        image_from_frontend.save(temp_path)

        destination_blob_name = (
            f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        )
        # gcs_path = upload_to_gcs(
        #     source_file_path=temp_path,
        #     destination_blob_name=destination_blob_name,
        # )
        image_id = str(uuid.uuid4())
        # add_image(
        #     image_id=image_id,
        #     s3_link=gcs_path,
        #     upload_date=datetime.now(),
        #     update_date=datetime.now(),
        #     label="",
        #     img_type="feedback",
        # )
        # new_image = get_image(image_id)
        # if not new_image:
        #     return JSONResponse(status_code=404, content={"message": "Image not found"})

        return JSONResponse(
            {
                "prediction": DUMMY_CLASS,
                "confidence": dummy_confidence,
                # "image_id": new_image["image_id"],
            }
        )

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
        image_id = str(uuid.uuid4())
        add_image(
            image_id=image_id,
            s3_link=gcs_path,
            upload_date=datetime.now(),
            update_date=datetime.now(),
            label="",
            img_type="feedback",
        )
        new_image = get_image(image_id)
        if not new_image:
            return JSONResponse(status_code=404, content={"message": "Image not found"})
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
            json={"uri": new_image["s3_link"]},
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
                "image_id": new_image["image_id"],
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

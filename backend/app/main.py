import base64
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Dict, Union

import torch
import torch.nn.functional as F
from numpy import ndarray

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from training.inference_engine.tensor_rt_inference import BrainTumorClassifier


class TestRequest(BaseModel):
    test2: str


# model = BrainTumorClassifier("./brain_tumor.engine")

root_dir = Path(__file__).parent.parent.parent
print("root_dir: ", root_dir)
sample_test_image = "training/brain_tumor_dataset/Testing/glioma_tumor/image(1).jpg"
image_path = Path(root_dir / sample_test_image)
image = Image.open(image_path).convert("RGB")

model_location = Path(root_dir / "training/inference_engine/brain_tumor_linux.engine")
print(model_location.exists())
print(model_location.absolute())
model = BrainTumorClassifier(model_location)


app = FastAPI(
    title="Medical Image Classification API",
    description="API for brain tumor image classification",
    version="1.0.0",
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning API status"""
    return {"status": "online", "message": "Medical Image Classification API"}


@app.post("/test")
async def test(test2: TestRequest):
    """sample endpoint with a request body"""
    print("hello from /test")
    print("test2: ", test2)
    return test2


@app.post("/api/predict")
async def predict_tumor_class(
    file: UploadFile = File(...),
):
    try:
        # Note: We won't use the base64 image for now, just the pillow image
        # contents = await file.read()
        # image_base64 = base64.b64encode(contents).decode("utf-8")

        contents = await file.read()
        image_from_frontend = Image.open(BytesIO(contents)).convert("RGB")

        # # foor dummy data image
        # print("image: ", image.size)
        # print("image: ", image.format)
        # print("image: ", image)

        output: ndarray = model.inference(image_from_frontend)
        print("output: ", output)
        print("output dimensions: ", output.shape)

        # Apply softmax to get probabilities
        probabilities = torch.nn.functional.softmax(torch.from_numpy(output), dim=1)
        confidence = probabilities.max().item()
        print("confidence: ", confidence)

        predicted_class_number = output.argmax().item()
        print(predicted_class_number)  # Output: 1

        # Mapping to label (optional):
        class_mapping = {
            0: "glioma_tumor",
            1: "meningioma_tumor",
            2: "no_tumor",
            3: "pituitary_tumor",
        }

        predicted_class = class_mapping[predicted_class_number]
        print("predicted_class", predicted_class)

        return JSONResponse(
            {
                "prediction": predicted_class,
                "confidence": confidence,  # Actual confidence score from model
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"Error processing image: {str(e)}"}
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

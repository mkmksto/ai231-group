import base64
from typing import Dict, Union

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class TestRequest(BaseModel):
    test2: str


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
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")

        # TODO: In the future, this base64 image will be sent to the ML model
        # For now, we'll return mock predictions

        return JSONResponse(
            {
                "prediction": "glioma_tumor",  # Mock prediction
                "confidence": 0.95,  # Mock confidence score
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

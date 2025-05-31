from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gcs_bucket import load_image_from_gcs
from PIL import Image
from pydantic import BaseModel

from app.inference import BrainTumorClassifier

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model = BrainTumorClassifier("brain_tumor_classifier.onnx")


class GCSRequest(BaseModel):
    uri: str


@app.get("/")
def read_root():
    return {"status": "Brain Tumor Classifier API is running."}


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post("/predict/gcs")
def predict_from_gcs(req: GCSRequest):
    print("inside predict_from_gcs")
    print("req.uri: ", req.uri)
    try:
        print("...inside try")
        image = load_image_from_gcs(req.uri)
        print("...after image loading")
        # print("image.encoder_info: ", image.encoderinfo)
        result = model.predict(image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

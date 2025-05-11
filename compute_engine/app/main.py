from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

from inference import BrainTumorClassifier
from gcs_bucket import load_image_from_gcs
    
app = FastAPI()
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
    try:
        image = load_image_from_gcs(req.uri)
        result = model.predict(image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
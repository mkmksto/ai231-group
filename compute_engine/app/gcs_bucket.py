import io
from PIL import Image
import requests
from google.cloud import storage

def load_image_from_gcs(gcs_uri: str) -> Image.Image:
    if gcs_uri.startswith("gs://"):
        bucket_name, blob_path = gcs_uri[5:].split("/", 1)
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        image_bytes = blob.download_as_bytes()
    else:
        # Assume it's a signed HTTPS URL
        response = requests.get(gcs_uri)
        response.raise_for_status()
        image_bytes = response.content

    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
import base64
import io
import json
import os

import requests
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image

BUCKET_NAME = os.getenv("BUCKET_NAME")
CREDENTIALS_FILE_BASE_64 = os.getenv("CREDENTIALS_FILE_BASE_64")
if not BUCKET_NAME or not CREDENTIALS_FILE_BASE_64:
    raise ValueError("BUCKET_NAME or CREDENTIALS_FILE is not set")


def get_storage_client():
    if CREDENTIALS_FILE_BASE_64:
        credentials_json = base64.b64decode(CREDENTIALS_FILE_BASE_64).decode("utf-8")
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info
        )
        return storage.Client(credentials=credentials)
    else:
        # Fallback to default credentials (useful for local development)
        return storage.Client()


def load_image_from_gcs(gcs_uri: str) -> Image.Image:
    print("inside load_image_from_gcs")
    try:
        if gcs_uri.startswith("gs://"):
            print("gcs uri startswith gs://")
            bucket_name, blob_path = gcs_uri[5:].split("/", 1)
            print("blob path: ", blob_path)
            # client = storage.Client()
            client = get_storage_client()
            # bucket = client.bucket(bucket_name)
            bucket = client.bucket(BUCKET_NAME)
            blob = bucket.blob(blob_path)
            image_bytes = blob.download_as_bytes()
        else:
            print("gcs uri does not start with gs://")
            # Assume it's a signed HTTPS URL
            response = requests.get(gcs_uri)
            response.raise_for_status()
            image_bytes = response.content
    except Exception as e:
        print("error: ", e)
        raise e

    return Image.open(io.BytesIO(image_bytes)).convert("RGB")

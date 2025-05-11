import base64
import json
import os

from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

load_dotenv()

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


def upload_to_gcs(
    source_file_path: str,
    destination_blob_name: str,
):
    storage_client = get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    # print(f"uploaded to gs://{BUCKET_NAME}/{destination_blob_name}")
    return f"gs://{BUCKET_NAME}/{destination_blob_name}"


def download_image(source_blob_name: str, destination_file_path: str) -> None:
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_path)


def update_blob_metadata(blob_name: str, metadata: dict) -> None:
    storage_client = get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    # Get existing metadata
    blob.reload()
    current_metadata = blob.metadata or {}
    print("current_metadata: ", current_metadata)

    # Update with new metadata
    current_metadata.update(metadata)
    print("updated metadata: ", current_metadata)

    # Set the updated metadata
    blob.metadata = current_metadata
    blob.patch()

# backend/app/pdf_ingest.py
import os
from dotenv import load_dotenv # type: ignore
from langchain_community.document_loaders import PyPDFLoader # type: ignore

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")  # optional
USE_S3 = bool(S3_BUCKET)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file_locally(file_bytes: bytes, filename: str) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path

def upload_to_s3(local_path: str, key: str):
    import boto3 # type: ignore
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    s3.upload_file(local_path, S3_BUCKET, key)
    # return https URL (or s3:// URI)
    return f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"

def process_pdf(file_path: str):
    """
    Processes a PDF file and returns the loaded documents.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Recording
import uuid
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/recordings")

# R2 configuration from environment
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT   = os.getenv("R2_ENDPOINT")
R2_BUCKET     = os.getenv("R2_BUCKET")

if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_ENDPOINT, R2_BUCKET]):
    raise RuntimeError("R2 environment variables are not loaded correctly")

s3 = boto3.client(
    service_name="s3",
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    endpoint_url=R2_ENDPOINT,
    region_name="auto"
)

@router.post("/upload")
async def upload_recording(
    sentence_id: str = Form(...),
    speaker_id: str  = Form(...),
    duration: int    = Form(...),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    filename = f"{speaker_id}_{sentence_id}_{uuid.uuid4().hex[:6]}.webm"

    # Upload file directly to R2
    s3.upload_fileobj(audio.file, R2_BUCKET, filename)

    # Save metadata in DB
    db.add(Recording(
        sentence_id=sentence_id,
        speaker_id=speaker_id,
        filename=filename,
        duration_sec=duration
    ))
    await db.commit()

    return {"status": "saved", "filename": filename}
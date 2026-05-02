from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Recording
import uuid
import boto3
import os
import asyncio
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(prefix="/api/recordings")

_MIME_MAP = {
    "audio/webm":             (".webm", "audio/webm"),
    "audio/webm;codecs=opus": (".webm", "audio/webm; codecs=opus"),
    "audio/ogg":              (".ogg",  "audio/ogg"),
    "audio/ogg;codecs=opus":  (".ogg",  "audio/ogg; codecs=opus"),
    "audio/mp4":              (".mp4",  "audio/mp4"),
    "audio/mpeg":             (".mp3",  "audio/mpeg"),
}

def _resolve_mime(raw: str) -> tuple[str, str]:
    key = raw.strip().lower().replace(" ", "")
    return _MIME_MAP.get(key, (".webm", "audio/webm"))

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
    mime_type: str   = Form(default="audio/webm"),
    split: str       = Form(default="train"),        # ← NEW
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    ext, content_type = _resolve_mime(mime_type)
    filename = f"{speaker_id}_{sentence_id}_{uuid.uuid4().hex[:6]}{ext}"

    try:
        await asyncio.to_thread(
            s3.upload_fileobj,
            audio.file,
            R2_BUCKET,
            filename,
            ExtraArgs={"ContentType": content_type},
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"R2 upload failed: {e}")

    try:
        db.add(Recording(
            sentence_id=sentence_id,
            speaker_id=speaker_id,
            filename=filename,
            duration_sec=duration,
            split=split                              # ← NEW
        ))
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB commit failed: {e}")

    return {"status": "saved", "filename": filename}
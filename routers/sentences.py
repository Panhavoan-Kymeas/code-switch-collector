from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Sentence, Recording

router = APIRouter(prefix="/api/sentences")


@router.get("/next")
async def get_next_sentence(speaker_id: str, db: AsyncSession = Depends(get_db)):
    already_recorded = (
        select(Recording.sentence_id)
        .where(Recording.speaker_id == speaker_id)
    )

    stmt = (
        select(Sentence)
        .outerjoin(Recording, Recording.sentence_id == Sentence.id)
        .where(Sentence.id.not_in(already_recorded))
        .group_by(Sentence.id, Sentence.text)
        .order_by(func.count(Recording.id).asc(), func.random())
        .limit(1)
    )

    result = await db.execute(stmt)
    sentence = result.scalar_one_or_none()

    if not sentence:
        return None

    return {"id": sentence.id, "text": sentence.text}
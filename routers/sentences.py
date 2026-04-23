from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Sentence, Recording
import random
import math

router = APIRouter(prefix="/api/sentences")


@router.get("/next")
async def get_next_sentence(speaker_id: str, db: AsyncSession = Depends(get_db)):
    already_recorded = (
        select(Recording.sentence_id)
        .where(Recording.speaker_id == speaker_id)
    )

    total_sentences_result = await db.execute(select(func.count(Sentence.id)))
    total_sentences = total_sentences_result.scalar_one()
    midpoint = max(1, total_sentences // 2)

    stmt = (
        select(
            Sentence,
            func.count(Recording.id).label("recording_count")
        )
        .outerjoin(Recording, Recording.sentence_id == Sentence.id)
        .where(Sentence.id.not_in(already_recorded))
        .group_by(Sentence.id, Sentence.text)
        .order_by(func.count(Recording.id).asc(), func.random())
        .limit(40)
    )

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return None

    sentences = []
    weights = []

    for sentence, recording_count in rows:
        num = int(sentence.id[1:])  # "S001" -> 1
        quality_weight = 1.0 if num <= midpoint else 0.45
        balance_weight = 1.0 / math.sqrt(recording_count + 1)
        final_weight = quality_weight * balance_weight

        sentences.append(sentence)
        weights.append(final_weight)

    chosen = random.choices(sentences, weights=weights, k=1)[0]

    return {"id": chosen.id, "text": chosen.text}
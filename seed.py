import csv
import re
import asyncio
from database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, Sentence

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def wrap_english(text):
    pattern = r'[A-Za-z0-9][A-Za-z0-9\']*(?:\s+[A-Za-z0-9][A-Za-z0-9\']*)*'
    return re.sub(pattern, lambda m: f'<span class="en">{m.group(0)}</span>', text)

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        with open("data/sentences.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sentence = Sentence(
                    id=row["id"],
                    text=wrap_english(row["text"]),
                    category=row["domain"]
                )
                db.add(sentence)
        await db.commit()
        print(f"✓ Seeded successfully")

asyncio.run(seed())

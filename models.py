from sqlalchemy import Column, String, Integer, DateTime
from database import Base  # <- use the Base from database.py
from datetime import datetime

class Sentence(Base):
    __tablename__ = "sentences"
    id = Column(String, primary_key=True)
    text = Column(String)
    category = Column(String)

class Recording(Base):
    __tablename__ = "recordings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(String)
    speaker_id = Column(String)
    filename = Column(String)
    duration_sec = Column(Integer)
    split = Column(String, default="train")
    created_at = Column(DateTime, default=datetime.utcnow)
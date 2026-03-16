from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase): pass

class Sentence(Base):
    __tablename__ = "sentences"
    id          = Column(String, primary_key=True)   # S001, S045...
    text        = Column(String)
    category    = Column(String)

class Recording(Base):
    __tablename__ = "recordings"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id  = Column(String)
    speaker_id   = Column(String)
    filename     = Column(String)
    duration_sec = Column(Integer)
    created_at   = Column(DateTime, default=datetime.utcnow)

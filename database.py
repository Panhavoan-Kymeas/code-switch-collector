from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read DATABASE_URL from environment, fallback to default SQLite if not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./voice_collector.db")

# Create engine and sessionmaker
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
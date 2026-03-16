from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import sentences, recordings
from database import engine, Base
from models import Sentence, Recording  # <- important!

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(sentences.router)
app.include_router(recordings.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def on_startup():
    try:
        async with engine.connect() as conn:  # use connect instead of begin
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
    except Exception as e:
        print("Failed to create tables:", e)
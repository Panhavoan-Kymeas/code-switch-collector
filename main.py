from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import sentences, recordings
from database import engine, Base

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(sentences.router)
app.include_router(recordings.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # This will create all tables defined in your models if they don't exist
        await conn.run_sync(Base.metadata.create_all)

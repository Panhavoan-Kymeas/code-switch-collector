from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import sentences, recordings

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(sentences.router)
app.include_router(recordings.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

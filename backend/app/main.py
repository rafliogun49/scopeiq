import pathlib

from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent.parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, projects, runs
from app.core.config import settings

app = FastAPI(title="ScopeIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(runs.router, prefix="/api/v1", tags=["runs"])
app.include_router(chat.router, prefix="/api/v1/projects", tags=["chat"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
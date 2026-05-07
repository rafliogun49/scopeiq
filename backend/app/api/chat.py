"""Chat endpoints (RAG Q&A) — implemented by Member B."""
from fastapi import APIRouter

router = APIRouter()


# TODO (B): GET /{id}/messages, POST /{id}/chat
# Each chat turn: retrieve top-k chunks → LLM answers with citations.
# See PRD §15 Chat section and §9 for chat endpoint spec.

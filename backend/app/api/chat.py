"""Chat endpoints (RAG Q&A) — implemented by Member B."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.chat import ChatMessage
from app.models.run import Run
from app.rag.retrieval import query as rag_query

router = APIRouter()

_openai: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _openai
    if _openai is None:
        _openai = AsyncOpenAI()
    return _openai


class ChatRequest(BaseModel):
    message: str


@router.get("/{project_id}/messages")
def get_messages(
    project_id: UUID,
    session: Session = Depends(get_session),
) -> list[ChatMessage]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.project_id == project_id)
        .order_by(ChatMessage.created_at)
    )
    return list(session.exec(statement).all())


@router.post("/{project_id}/chat")
async def chat(
    project_id: UUID,
    body: ChatRequest,
    session: Session = Depends(get_session),
) -> dict:
    if not body.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    latest_run = session.exec(
        select(Run)
        .where(Run.project_id == project_id, Run.status == "completed")
        .order_by(desc(Run.__table__.c.created_at))
    ).first()

    if not latest_run:
        raise HTTPException(
            status_code=400,
            detail="No completed run found for this project. Please run research first.",
        )

    user_msg = ChatMessage(
        project_id=project_id,
        role="user",
        content=body.message,
        citations=[],
    )
    session.add(user_msg)
    session.flush()

    try:
        chunks = await rag_query(run_id=latest_run.id, query_text=body.message)
    except Exception:
        chunks = []

    client = get_openai_client()

    if chunks:
        context = "\n\n".join(
            [f"[Source: {c['source_url']}]\n{c['chunk']}" for c in chunks]
        )
        citations = [
            {"chunk": c["chunk"], "source_url": c["source_url"], "score": c["score"]}
            for c in chunks
        ]

        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful research assistant for ScopeIQ. "
                        "Answer the user's question based ONLY on the provided research context. "
                        "Be concise, specific, and actionable. "
                        "IMPORTANT: You MUST respond in the EXACT same language as the user's question. "
                        "If the user writes in Bahasa Indonesia, respond in Bahasa Indonesia. "
                        "If the user writes in English, respond in English. "
                        "Never switch languages."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Research context:\n{context}\n\n"
                        f"User question (answer in the same language as this question): {body.message}"
                    ),
                },
            ],
        )
        answer = resp.choices[0].message.content or ""

    else:
        answer = (
            "Tidak ada data relevan ditemukan untuk pertanyaan ini. "
            "Pastikan research sudah selesai dijalankan."
        )
        citations = []

    assistant_msg = ChatMessage(
        project_id=project_id,
        role="assistant",
        content=answer,
        citations=citations,
    )
    session.add(assistant_msg)
    session.commit()
    session.refresh(assistant_msg)

    return {"assistant_message": assistant_msg.content, "citations": citations}

"""pgvector retrieval — B-PR1."""
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Session

from app.core.db import engine
from app.rag.embedding import embed_batch


async def query(run_id: UUID, query_text: str, top_k: int = 8) -> list[dict]:
    """Cosine similarity search di pgvector, scoped per run_id."""

    # Embed query
    vectors = await embed_batch([query_text])
    query_vector = vectors[0]

    sql = text("""
        SELECT
            text,
            source_url,
            1 - (embedding <=> CAST(:vec AS vector)) AS score
        FROM chunk
        WHERE run_id = :run_id
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :top_k
    """)

    with Session(engine) as session:
        rows = session.exec(  # type: ignore
            sql,
            params={
                "vec": str(query_vector),
                "run_id": str(run_id),
                "top_k": top_k,
            },
        ).fetchall()

    return [
        {"chunk": row.text, "source_url": row.source_url, "score": float(row.score)}
        for row in rows
    ]
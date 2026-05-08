"""RAG indexing entry point — B-PR1."""
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.models.chunk import Chunk
from app.rag.chunking import chunk_text
from app.rag.embedding import embed_batch
from app.schemas.rag import RawDoc


async def index_chunks(run_id: UUID, docs: list[RawDoc]) -> int:
    """Chunk → embed → simpan ke pgvector. Returns total chunks indexed."""

    # 1. Chunking semua dokumen — simpan teks + metadata dulu
    all_texts: list[str] = []
    all_meta: list[dict] = []

    for doc in docs:
        for t in chunk_text(doc.text):
            all_texts.append(t)
            all_meta.append({
                "source_url": doc.url,
                "source_type": doc.source_type,
                "competitor": doc.competitor,
            })

    if not all_texts:
        return 0

    # 2. Embed semua sekaligus (batched)
    vectors = await embed_batch(all_texts)

    # 3. Buat Chunk dengan embedding langsung tersedia
    all_chunks = [
        Chunk(
            run_id=run_id,
            text=text,
            embedding=vector,
            source_url=meta["source_url"],
            source_type=meta["source_type"],
            competitor=meta["competitor"],
        )
        for text, vector, meta in zip(all_texts, vectors, all_meta)
    ]

    # 4. Bulk insert ke database
    with Session(engine) as session:
        session.add_all(all_chunks)
        session.commit()

    return len(all_chunks)
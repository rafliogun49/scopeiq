"""rag_query MCP tool — interface contract §7.4."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uuid import UUID

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

from app.rag.retrieval import query as rag_retrieval


async def rag_query(query: str, run_id: str, top_k: int = 8) -> list[dict]:
    """Vector search scoped to run_id. Returns ranked chunks with source URLs."""
    results = await rag_retrieval(
        run_id=UUID(run_id),
        query_text=query,
        top_k=top_k,
    )
    return results

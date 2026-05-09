"""pgvector retrieval — implemented in B-PR1.

Vector search scoped to a specific run_id.
Called by the chat endpoint and (via MCP rag_query) by the Synthesizer.
See PRD §11 and TEAM_SPLIT §4 (B-PR1).
"""

from uuid import UUID

# TODO (B-PR1): cosine similarity search on Chunk.embedding with run_id filter
# Acceptance: retrieval returns expected chunk for known fixture


async def query(run_id: UUID, text: str, top_k: int = 8) -> list[dict]:
    """Returns [{chunk, source_url, score}] scoped to run_id."""
    raise NotImplementedError

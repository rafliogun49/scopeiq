"""RAG indexing entry point — implements interface contract §7.1.

Called by A's agents after Scraper / Social finish fetching.
B owns the implementation; A imports index_chunks from here.

Lock the signature by Day 2 (both sides import this module).
See PRD §11 and TEAM_SPLIT §7.1.
"""
from uuid import UUID

from app.schemas.rag import RawDoc

# TODO (B-PR1): implement chunking → embedding → pgvector insert
# Acceptance: unit test inserts 3 fixture docs → query returns the right one in top-1


async def index_chunks(run_id: UUID, docs: list[RawDoc]) -> int:
    """Chunk, embed, and store docs. Returns number of chunks indexed."""
    raise NotImplementedError

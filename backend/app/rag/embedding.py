"""OpenAI embedding wrapper — implemented in B-PR1.

Calls text-embedding-3-small, batched for efficiency.
Output: list of 1536-dim float vectors.
See PRD §11 and TEAM_SPLIT §4 (B-PR1).
"""
# TODO (B-PR1): call openai.embeddings.create, batch in groups of 100
# Acceptance: embedding shape is 1536 (unit test in tests/test_rag.py)


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Returns one 1536-dim vector per input text."""
    raise NotImplementedError

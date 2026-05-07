"""Token-aware text chunker — implemented in B-PR1.

Splits text into chunks of ~800 tokens with 100-token overlap.
See PRD §11 (Indexing pipeline) and TEAM_SPLIT §4 (B-PR1).
"""
# TODO (B-PR1): implement using tiktoken or a similar tokenizer
# Acceptance: chunk boundaries respect token limits (unit test in tests/test_rag.py)


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into token-aware chunks."""
    raise NotImplementedError

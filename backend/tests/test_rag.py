"""RAG unit tests — B-PR1."""
import pytest
from unittest.mock import AsyncMock, patch
from app.rag.chunking import chunk_text
from app.rag.embedding import embed_batch
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


# ── Chunking tests ────────────────────────────────────────────────────────────

def test_chunk_respects_token_limit():
    long_text = "hello world " * 1000  # ~2000 tokens
    chunks = chunk_text(long_text, size=800, overlap=100)
    for c in chunks:
        assert len(_enc.encode(c)) <= 800


def test_chunk_overlap():
    long_text = "token " * 1000
    chunks = chunk_text(long_text, size=800, overlap=100)
    assert len(chunks) >= 2  # harus lebih dari 1 chunk


def test_short_text_single_chunk():
    short = "hello world"
    chunks = chunk_text(short)
    assert len(chunks) == 1


# ── Embedding tests ───────────────────────────────────────────────────────────

def _make_mock_response(num_texts: int, dim: int = 1536):
    """Create a mock OpenAI embedding response."""
    items = []
    for _ in range(num_texts):
        item = type('obj', (object,), {'embedding': [0.0] * dim})
        items.append(item)
    return type('obj', (object,), {'data': items})


@pytest.mark.asyncio
async def test_embedding_shape():
    with patch("app.rag.embedding.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.embeddings.create = AsyncMock(
            return_value=_make_mock_response(1)
        )
        mock_get_client.return_value = mock_client

        vectors = await embed_batch(["test embedding shape"])
        assert len(vectors) == 1
        assert len(vectors[0]) == 1536


@pytest.mark.asyncio
async def test_embedding_batch():
    with patch("app.rag.embedding.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.embeddings.create = AsyncMock(
            return_value=_make_mock_response(3)
        )
        mock_get_client.return_value = mock_client

        texts = ["text one", "text two", "text three"]
        vectors = await embed_batch(texts)
        assert len(vectors) == 3
        for v in vectors:
            assert len(v) == 1536
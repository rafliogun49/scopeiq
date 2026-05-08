"""OpenAI embedding wrapper — B-PR1."""
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None
_MODEL = "text-embedding-3-small"
_BATCH = 100


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()  # baca OPENAI_API_KEY dari env saat pertama dipanggil
    return _client


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Returns one 1536-dim vector per input text, batched per 100."""
    client = get_client()
    results: list[list[float]] = []

    for i in range(0, len(texts), _BATCH):
        batch = texts[i : i + _BATCH]
        response = await client.embeddings.create(model=_MODEL, input=batch)
        results.extend([item.embedding for item in response.data])

    return results
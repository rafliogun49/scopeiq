"""Token-aware text chunker — B-PR1."""
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into token-aware chunks with overlap."""
    tokens = _enc.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + size
        chunk_tokens = tokens[start:end]
        chunks.append(_enc.decode(chunk_tokens))
        if end >= len(tokens):
            break
        start += size - overlap  # geser mundur sebesar overlap

    return chunks
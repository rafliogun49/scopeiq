"""Seed Langfuse with the local prompt files.

Run once (or whenever you update a local .md file and want to push it):

    uv run python scripts/seed_langfuse_prompts.py

The script creates or updates two text prompts in Langfuse:
  - scopeiq-orchestrator   (from prompts/orchestrator.md)
  - scopeiq-scraper        (from prompts/scraper.md)

After this, the agents will pull the live versions from Langfuse on every run
(with a 60-second cache). You can then edit them in the Langfuse UI without
redeploying.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure app config is importable from the backend/ root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402 — path must be set first

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROMPT_MAP = {
    "scopeiq-orchestrator": PROMPTS_DIR / "orchestrator.md",
    "scopeiq-scraper": PROMPTS_DIR / "scraper.md",
}


def main() -> None:
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        print("ERROR: LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY not set in .env")
        sys.exit(1)

    from langfuse import Langfuse

    client = Langfuse(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
    )

    for prompt_name, path in PROMPT_MAP.items():
        if not path.exists():
            print(f"  SKIP  {prompt_name} — file not found: {path}")
            continue

        text = path.read_text(encoding="utf-8")
        client.create_prompt(
            name=prompt_name,
            prompt=text,
            type="text",
            labels=["production"],
        )
        print(f"  OK    {prompt_name} ({len(text)} chars) → {settings.LANGFUSE_HOST}")

    client.flush()
    print("Done.")


if __name__ == "__main__":
    main()

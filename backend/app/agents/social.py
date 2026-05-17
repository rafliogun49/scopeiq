"""Social agent — B-PR3."""

import pathlib
from uuid import UUID

from agents import Agent, Runner, function_tool
from langfuse import Langfuse

from app.rag.index import index_chunks  # ← tambah ini
from app.schemas.rag import RawDoc  # ← tambah ini
from app.tools.hn import hn_search
from app.tools.stackexchange import stackexchange_search
from app.tools.tavily import tavily_search

_PROMPT = (pathlib.Path(__file__).parent.parent.parent / "prompts" / "social.md").read_text()
_langfuse = Langfuse()
VALID_THEMES = {"pricing", "UX", "sync", "support", "missing-feature"}


# ── Theme Classification ──────────────────────────────────────────────────────

_THEME_KEYWORDS: dict[str, list[str]] = {
    "pricing": ["price", "pricing", "expensive", "cost", "cheap", "plan", "subscription", "pay", "billing", "fee"],
    "UX": ["ux", "ui", "interface", "design", "confus", "hard to use", "difficult", "clunky", "slow", "ugly"],
    "sync": ["sync", "offline", "real-time", "realtime", "lag", "delay", "update", "refresh", "conflict"],
    "support": ["support", "help", "customer service", "response", "ticket", "documentation", "docs"],
    "missing-feature": ["missing", "lack", "wish", "want", "feature", "request", "need", "should have", "would love"],
}


def classify_theme(text: str) -> str:
    """Fast keyword-based theme classifier — no API calls."""
    lower = text.lower()
    scores = {theme: sum(1 for kw in kws if kw in lower) for theme, kws in _THEME_KEYWORDS.items()}
    best = max(scores, key=lambda t: scores[t])
    return best if scores[best] > 0 else "UX"


async def classify_snippets(snippets: list[dict]) -> list[dict]:
    for s in snippets:
        s["theme"] = classify_theme(s.get("snippet") or s.get("text", ""))
    return snippets


# ── Function Tools ────────────────────────────────────────────────────────────


@function_tool
async def tool_tavily_search(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[dict]:
    """Cari artikel, review, dan thread dari domain tertentu."""
    results = await tavily_search(query, max_results, include_domains, exclude_domains)
    return await classify_snippets(results)


@function_tool
async def tool_hn_search(query: str, limit: int = 10) -> list[dict]:
    """Cari thread di Hacker News via Algolia."""
    results = await hn_search(query, limit)
    return await classify_snippets(results)


@function_tool
async def tool_stackexchange_search(
    query: str,
    sites: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """Cari pertanyaan di Stack Exchange."""
    results = await stackexchange_search(query, sites, limit)
    return await classify_snippets(results)


# ── Agent ─────────────────────────────────────────────────────────────────────

social_agent = Agent(
    name="SocialAgent",
    model="gpt-4o-mini",
    instructions=_PROMPT,
    tools=[tool_tavily_search, tool_hn_search, tool_stackexchange_search],
)


# ── Entry point dengan Langfuse + post-finish chunking ────────────────────────


async def run_social(query: str, run_id: str | None = None) -> str:  # ← tambah run_id
    """Entry point dengan Langfuse tracing + index chunks ke pgvector."""
    with _langfuse.start_as_current_observation(
        as_type="agent",
        name="social-agent",
        input={"query": query},
    ):
        result = await Runner.run(social_agent, input=query)
        output = result.final_output

        # ── Wire post-finish chunking ─────────────────────────────────────────
        if run_id:
            # Kumpulkan semua tool results dari agent sebagai RawDoc
            raw_docs = [
                RawDoc(
                    url="https://social-agent-output",
                    text=output,
                    source_type="community",
                )
            ]
            indexed = await index_chunks(UUID(run_id), raw_docs)
            print(f"[Social] Indexed {indexed} chunks to pgvector")

        _langfuse.set_current_trace_io(
            input={"query": query},
            output={"result": output[:200]},
        )

    return output

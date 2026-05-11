"""Synthesizer agent — B-PR4."""

import json
import pathlib
from uuid import UUID

from agents import (
    Agent,
    ModelSettings,
    Runner,
    function_tool,
)
from dotenv import load_dotenv
from langfuse import Langfuse

from app.rag.retrieval import query as _rag_query
from mcp_server.python_exec import python_exec as _python_exec

load_dotenv(pathlib.Path(__file__).parent.parent.parent.parent / ".env")

# Load prompt
_PROMPT = (pathlib.Path(__file__).parent.parent.parent / "prompts" / "synthesizer.md").read_text()

# Langfuse client
_langfuse = Langfuse()


# ── Function Tools ────────────────────────────────────────────────────────────


@function_tool
async def rag_query(query: str, run_id: str, top_k: int = 8) -> str:
    """Retrieve evidence from pgvector corpus scoped to run_id."""
    results = await _rag_query(
        run_id=UUID(run_id),
        query_text=query,
        top_k=top_k,
    )
    return json.dumps(results, ensure_ascii=False)


@function_tool
async def python_exec(code: str, dataset_json: str = "{}") -> str:
    """Run Python in sandbox to generate charts. Returns {stdout, charts}."""
    result = await _python_exec(code=code, dataset_id=dataset_json)
    return json.dumps(result, ensure_ascii=False)


# ── Agent ─────────────────────────────────────────────────────────────────────

synthesizer_agent = Agent(
    name="SynthesizerAgent",
    model="gpt-4o",
    instructions=_PROMPT,
    tools=[rag_query, python_exec],
    model_settings=ModelSettings(temperature=0),  # deterministic — hasil konsisten tiap run
)


# ── Validation helper ─────────────────────────────────────────────────────────


def _report_valid(report: str) -> bool:
    """
    Return True jika report memenuhi semua acceptance criteria:
      1. >= 800 kata
      2. Semua 4 seksi hadir (cek dengan multiple alias per seksi)
    """
    r = report.lower()
    has_s1 = any(
        x in r
        for x in [
            "real market",
            "is the market",
            "is this a real",
            "market size",
            "market validation",
            "market opportunity",
        ]
    )
    has_s2 = any(
        x in r
        for x in [
            "already there",
            "who's already",
            "competitive landscape",
            "competitors",
            "existing players",
            "existing solutions",
        ]
    )
    has_s3 = any(
        x in r
        for x in [
            "users hate",
            "what do users",
            "complaints",
            "pain points",
            "frustrations",
            "users dislike",
            "user complaints",
        ]
    )
    has_s4 = any(
        x in r
        for x in [
            "gap",
            "opportunity",
            "where's the",
            "where is the",
        ]
    )
    word_count = len(report.split())
    return word_count >= 800 and all([has_s1, has_s2, has_s3, has_s4])


# ── Entry point ───────────────────────────────────────────────────────────────


async def run_synthesizer(run_id: str, idea: str) -> str:
    """
    Entry point dipanggil oleh Orchestrator.
    - Langfuse tracing via start_as_current_observation (v4 API)
    - Retry hingga 3x jika output tidak valid (word count < 800 atau seksi hilang)
    - temperature=0 pada agent untuk hasil yang konsisten
    """

    base_prompt = f"""
Idea being validated: **{idea}**
Run ID for rag_query: `{run_id}`

Write the complete 4-section research report as instructed.
Use rag_query for each section to ground all claims in real evidence.
IMPORTANT: Each section MUST be at least 200 words. Total MUST exceed 900 words.
"""

    with _langfuse.start_as_current_observation(
        as_type="agent",
        name="synthesizer-agent",
        input={"idea": idea, "run_id": run_id},
    ):
        prompt = base_prompt
        report = ""

        for attempt in range(3):  # max 3 attempts
            result = await Runner.run(synthesizer_agent, input=prompt)
            report = result.final_output or ""

            if _report_valid(report):
                break  # sukses — keluar dari loop

            if attempt < 2:
                word_count = len(report.split())
                # Retry dengan instruksi eksplisit: enforce section headers + word count
                prompt = (
                    base_prompt + f"\n\nWARNING (attempt {attempt + 2}/3): "
                    f"Previous response had {word_count} words and/or missing sections. "
                    "You MUST:\n"
                    "1. Use EXACTLY these section headers:\n"
                    "   ## Is This a Real Market?\n"
                    "   ## Who's Already There?\n"
                    "   ## What Do Users Hate?\n"
                    "   ## Where's the Gap?\n"
                    "2. Write at least 225 words per section\n"
                    "3. Total must exceed 900 words\n"
                    "Start your response directly with the first section header."
                )

        _langfuse.set_current_trace_io(
            input={"idea": idea, "run_id": run_id},
            output={"word_count": len(report.split()), "preview": report[:200]},
        )

    return report

"""Synthesizer agent — B-PR4."""

import json
import pathlib
from uuid import UUID

from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent.parent.parent.parent / ".env")  # ← tambah ini

from agents import Agent, Runner, function_tool

from app.rag.retrieval import query as _rag_query
from mcp_server.python_exec import python_exec as _python_exec

# Load prompt
_PROMPT = (pathlib.Path(__file__).parent.parent.parent / "prompts" / "synthesizer.md").read_text()


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


synthesizer_agent = Agent(
    name="SynthesizerAgent",
    model="gpt-4o",
    instructions=_PROMPT,
    tools=[rag_query, python_exec],
)


async def run_synthesizer(run_id: str, idea: str) -> str:
    """Entry point called by Orchestrator. Returns Markdown report."""
    prompt = f"""
Idea being validated: **{idea}**
Run ID for rag_query: `{run_id}`

Write the complete 4-section research report as instructed.
Use rag_query for each section to ground all claims in real evidence.
"""
    result = await Runner.run(synthesizer_agent, input=prompt)
    return result.final_output

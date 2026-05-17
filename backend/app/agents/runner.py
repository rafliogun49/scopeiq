"""Agent runner facade — A-PR4.

Two execution paths:
  • real: the openai-agents SDK runs the Orchestrator → Scraper handoff.
  • stub: a deterministic Python loop calls the same plain tools (used in tests).

The stub mode keeps CI fast and free; production uses the real SDK.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.agents.scraper import SourceType, current_competitor_var, raw_docs_var
from app.core.observability import get_client, observe
from app.models.project import Project
from app.schemas.rag import RawDoc
from app.tools.discover_urls import discover_urls
from app.tools.extract_text import extract_text
from app.tools.http_fetch import http_fetch
from app.workers.budget import get_budget
from app.workers.run_events import emit_event, run_id_var

_USE_STUB = False


def use_stub_runner() -> None:
    global _USE_STUB
    _USE_STUB = True


def use_real_runner() -> None:
    global _USE_STUB
    _USE_STUB = False


def _classify_source(url: str) -> SourceType:
    path = url.lower()
    if "pricing" in path or "plans" in path:
        return "pricing"
    return "landing"


def _estimate_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Rough token estimate via tiktoken; falls back to word-count if unavailable."""
    try:
        import tiktoken

        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text.split()))


@observe(name="orchestrator_stub", as_type="agent")
async def _run_stub(project: Project) -> list[RawDoc]:
    docs: list[RawDoc] = []
    raw_docs_var.set(docs)
    budget = get_budget()

    emit_event("agent_started", agent="orchestrator", payload={"mode": "stub"})
    for competitor in project.known_competitors or []:
        current_competitor_var.set(competitor)
        emit_event("agent_started", agent="scraper", payload={"competitor": competitor})

        urls = await discover_urls(competitor)
        per_competitor: list[RawDoc] = []
        for url in urls:
            res = await http_fetch(url)
            html = res.get("html", "")
            if not html:
                continue
            extracted = extract_text(html, base_url=url)
            text = extracted["text"]
            if text:
                per_competitor.append(
                    RawDoc(
                        url=url,
                        text=text,
                        source_type=_classify_source(url),
                        competitor=competitor,
                    )
                )
                # Estimate tokens for the scraping prompt + extracted content.
                if budget is not None:
                    prompt = f"Scrape {url} for {competitor}"
                    budget.add_tokens(
                        input_tokens=_estimate_tokens(prompt),
                        output_tokens=_estimate_tokens(text),
                        model="gpt-4o-mini",
                    )
        docs.extend(per_competitor)
        emit_event(
            "agent_finished",
            agent="scraper",
            payload={"competitor": competitor, "docs": len(per_competitor)},
        )

    budget_payload: dict = {"docs": len(docs)}
    if budget is not None:
        budget_payload.update(
            {
                "tokens_in": budget.input_tokens,
                "tokens_out": budget.output_tokens,
                "cost_usd": round(budget.cost_usd, 6),
            }
        )
        get_client().update_current_span(
            metadata={
                "tokens_in": budget.input_tokens,
                "tokens_out": budget.output_tokens,
                "cost_usd": round(budget.cost_usd, 6),
                "docs_scraped": len(docs),
            }
        )
    emit_event("agent_finished", agent="orchestrator", payload=budget_payload)
    return docs


@observe(name="orchestrator_real", as_type="agent")
async def _run_real(project: Project) -> list[RawDoc]:
    from agents import AgentHooks, Runner

    from app.agents.orchestrator import orchestrator_agent
    from app.agents.scraper import scraper_agent
    from app.core.config import settings

    docs: list[RawDoc] = []
    raw_docs_var.set(docs)
    budget = get_budget()
    competitors = list(project.known_competitors or [])

    # Always enrich competitor list via Tavily — user-provided ones come first
    from urllib.parse import urlparse

    from app.tools.tavily import tavily_search

    search_results = await tavily_search(
        f"top competitors alternatives to {project.idea}", max_results=6
    )
    seen: set[str] = set(competitors)
    for r in search_results:
        domain = urlparse(r.get("url", "")).netloc.replace("www.", "")
        if domain and domain not in seen:
            seen.add(domain)
            competitors.append(domain)
    emit_event(
        "log",
        agent="orchestrator",
        payload={"discovered_competitors": competitors},
    )

    if competitors:
        current_competitor_var.set(competitors[0])

    class _Hooks(AgentHooks[Any]):
        def __init__(self, agent_name: str) -> None:
            self.agent_name = agent_name

        async def on_start(self, context, agent) -> None:  # type: ignore[override]
            if budget is not None:
                budget.check_turn(self.agent_name)
            emit_event("agent_started", agent=self.agent_name)

        async def on_end(self, context, agent, output) -> None:  # type: ignore[override]
            # Accumulate real token usage from the SDK's RunResult.
            if budget is not None:
                usage = getattr(output, "usage", None) or getattr(output, "raw_responses", None)
                if usage is not None and hasattr(usage, "input_tokens"):
                    budget.add_tokens(
                        input_tokens=usage.input_tokens,
                        output_tokens=usage.output_tokens,
                        model="gpt-4o-mini",
                    )
            payload: dict = {}
            if self.agent_name == "scraper":
                payload["docs"] = len(docs)
            if budget is not None:
                payload.update(
                    {
                        "tokens_in": budget.input_tokens,
                        "tokens_out": budget.output_tokens,
                        "cost_usd": round(budget.cost_usd, 6),
                    }
                )
            emit_event("agent_finished", agent=self.agent_name, payload=payload)

    orchestrator_agent.hooks = _Hooks("orchestrator")
    scraper_agent.hooks = _Hooks("scraper")

    prompt = (
        f"Product idea: {project.idea}\n"
        f"Known competitors: {', '.join(competitors) if competitors else '(none)'}\n\n"
        "Hand off to the Scraper. The Scraper should call discover_urls for each "
        "competitor, then http_fetch + extract_text on the URLs it returns."
    )
    await Runner.run(orchestrator_agent, input=prompt, max_turns=settings.MAX_AGENT_TURNS)
    if budget is not None:
        get_client().update_current_span(
            metadata={
                "tokens_in": budget.input_tokens,
                "tokens_out": budget.output_tokens,
                "cost_usd": round(budget.cost_usd, 6),
                "docs_scraped": len(docs),
            }
        )
    return docs


@observe(name="run_orchestrator", as_type="agent")
async def run_orchestrator(run_id: UUID, project: Project) -> list[RawDoc]:
    """Drive the agent pipeline for `project`, returning the scraped RawDocs."""
    run_id_var.set(run_id)
    if _USE_STUB:
        return await _run_stub(project)
    return await _run_real(project)

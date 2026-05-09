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
from app.models.project import Project
from app.schemas.rag import RawDoc
from app.tools.discover_urls import discover_urls
from app.tools.extract_text import extract_text
from app.tools.http_fetch import http_fetch
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


async def _run_stub(project: Project) -> list[RawDoc]:
    docs: list[RawDoc] = []
    raw_docs_var.set(docs)

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
            if extracted["text"]:
                per_competitor.append(
                    RawDoc(
                        url=url,
                        text=extracted["text"],
                        source_type=_classify_source(url),
                        competitor=competitor,
                    )
                )
        docs.extend(per_competitor)
        emit_event(
            "agent_finished",
            agent="scraper",
            payload={"competitor": competitor, "docs": len(per_competitor)},
        )

    emit_event("agent_finished", agent="orchestrator", payload={"docs": len(docs)})
    return docs


async def _run_real(project: Project) -> list[RawDoc]:
    from agents import AgentHooks, Runner

    from app.agents.orchestrator import orchestrator_agent
    from app.agents.scraper import scraper_agent

    docs: list[RawDoc] = []
    raw_docs_var.set(docs)
    competitors = list(project.known_competitors or [])
    if competitors:
        current_competitor_var.set(competitors[0])

    class _Hooks(AgentHooks[Any]):
        def __init__(self, agent_name: str) -> None:
            self.agent_name = agent_name

        async def on_start(self, context, agent) -> None:  # type: ignore[override]
            emit_event("agent_started", agent=self.agent_name)

        async def on_end(self, context, agent, output) -> None:  # type: ignore[override]
            payload = {"docs": len(docs)} if self.agent_name == "scraper" else {}
            emit_event("agent_finished", agent=self.agent_name, payload=payload)

    orchestrator_agent.hooks = _Hooks("orchestrator")
    scraper_agent.hooks = _Hooks("scraper")

    prompt = (
        f"Product idea: {project.idea}\n"
        f"Known competitors: {', '.join(competitors) if competitors else '(none)'}\n\n"
        "Hand off to the Scraper. The Scraper should call discover_urls for each "
        "competitor, then http_fetch + extract_text on the URLs it returns."
    )
    await Runner.run(orchestrator_agent, input=prompt)
    return docs


async def run_orchestrator(run_id: UUID, project: Project) -> list[RawDoc]:
    """Drive the agent pipeline for `project`, returning the scraped RawDocs."""
    run_id_var.set(run_id)
    if _USE_STUB:
        return await _run_stub(project)
    return await _run_real(project)

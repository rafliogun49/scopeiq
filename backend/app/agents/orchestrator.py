"""Orchestrator agent — A-PR4.

Plans the run and hands off to the Scraper agent. Uses gpt-4o-mini.

Out of scope for PR4 (added later): python_exec, Social agent handoff,
Synthesizer agent handoff. See PRD §10 and TEAM_SPLIT §3.
"""
from __future__ import annotations

from pathlib import Path

from agents import Agent, handoff

from app.agents.scraper import scraper_agent

_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "orchestrator.md"

orchestrator_agent = Agent(
    name="Orchestrator",
    model="gpt-4o-mini",
    instructions=_PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else "",
    handoffs=[handoff(scraper_agent)],
)

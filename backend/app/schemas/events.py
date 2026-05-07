"""Interface contract §7.2 — locked by Day 3 (pair: A + C).

Backend emits these as SSE data payloads; frontend mirrors in lib/sse.ts.
"""
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


EventType = Literal["plan", "agent_started", "tool_called", "agent_finished", "error", "log"]
AgentName = Literal["orchestrator", "scraper", "social", "synthesizer"] | None


class RunEvent(BaseModel):
    type: EventType
    agent: AgentName = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunCompleteEvent(BaseModel):
    run_id: UUID
    status: Literal["completed", "failed", "cancelled"]

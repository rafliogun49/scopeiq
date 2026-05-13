"""Run event emission helper — A-PR4.

Tools and the agent runner use a contextvar-bound run_id so they can insert
RunEvent rows without threading session/run_id through their signatures.
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import Any
from uuid import UUID

from sqlmodel import Session

from app.models.run import RunEvent

run_id_var: ContextVar[UUID | None] = ContextVar("scopeiq_run_id", default=None)


def emit_event(
    type: str,
    agent: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Insert a RunEvent for the current run. No-op when run_id_var is unset."""
    rid = run_id_var.get()
    if rid is None:
        return
    # Lazy import to avoid a tasks ↔ tools/agents ↔ run_events cycle, and so
    # tests/conftest.py's `monkeypatch.setattr(tasks_module, "engine", ...)` is
    # picked up at call time.
    from app.workers import tasks as tasks_module

    with Session(tasks_module.engine) as s:
        s.add(RunEvent(run_id=rid, type=type, agent=agent, payload=payload or {}))
        s.commit()

"""Runs endpoints + SSE stream — implemented in A-PR3 / A-PR4."""

import asyncio
import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, col, select

from app.api.deps import CurrentUserDep, SessionDep, StreamUserDep
from app.models.project import Project
from app.models.run import Run, RunEvent
from app.schemas.runs import (
    RunCancelResponse,
    RunCreateResponse,
    RunEventResponse,
    RunResponse,
)
from app.workers.tasks import run_research_task

router = APIRouter()

TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
STREAM_POLL_SECONDS = 0.5
STREAM_MAX_SECONDS = 600.0  # 10 min hard cap


def _load_owned_run(session: SessionDep, run_id: UUID, user_id: UUID) -> Run:
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    project = session.get(Project, run.project_id)
    if project is None or project.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.post(
    "/projects/{project_id}/runs",
    response_model=RunCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    project_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> RunCreateResponse:
    project = session.get(Project, project_id)
    if project is None or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    run = Run(project_id=project.id, status="pending")
    session.add(run)
    session.commit()
    session.refresh(run)
    run_research_task.delay(str(run.id))
    return RunCreateResponse(run_id=run.id, status=run.status)


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> Run:
    return _load_owned_run(session, run_id, current_user.id)


@router.post("/runs/{run_id}/cancel", response_model=RunCancelResponse)
def cancel_run(
    run_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> RunCancelResponse:
    run = _load_owned_run(session, run_id, current_user.id)
    if run.status in TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run is already {run.status}",
        )
    run.status = "cancelled"
    session.add(run)
    session.commit()
    session.refresh(run)
    return RunCancelResponse(status=run.status)


@router.get("/runs/{run_id}/events", response_model=list[RunEventResponse])
def list_run_events(
    run_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[RunEvent]:
    _load_owned_run(session, run_id, current_user.id)
    return list(
        session.exec(
            select(RunEvent)
            .where(RunEvent.run_id == run_id)
            .order_by(col(RunEvent.timestamp).asc())
            .offset(offset)
            .limit(limit)
        ).all()
    )


def _format_sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


def _serialize_event(event: RunEvent) -> str:
    return json.dumps(
        {
            "type": event.type,
            "agent": event.agent,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat(),
        }
    )


async def _stream_run_events(run_id: UUID):
    """Async generator: poll RunEvent rows + run status; yield SSE frames."""
    # Resolve engine lazily via tasks module so test fixtures (which monkeypatch
    # `tasks_module.engine` to the test DB) are picked up — same pattern as
    # app.workers.run_events.emit_event.
    from app.workers import tasks as tasks_module

    last_seen: datetime | None = None
    elapsed = 0.0
    while True:
        with Session(tasks_module.engine) as s:
            run = s.get(Run, run_id)
            if run is None:
                yield _format_sse(
                    "complete",
                    json.dumps({"run_id": str(run_id), "status": "failed"}),
                )
                return
            stmt = select(RunEvent).where(RunEvent.run_id == run_id)
            if last_seen is not None:
                stmt = stmt.where(col(RunEvent.timestamp) > last_seen)
            stmt = stmt.order_by(col(RunEvent.timestamp).asc())
            new_events = list(s.exec(stmt).all())
            run_status = run.status

        for event in new_events:
            last_seen = event.timestamp
            yield _format_sse("progress", _serialize_event(event))

        if run_status in TERMINAL_STATUSES:
            yield _format_sse(
                "complete",
                json.dumps({"run_id": str(run_id), "status": run_status}),
            )
            return

        if elapsed >= STREAM_MAX_SECONDS:
            yield _format_sse(
                "complete",
                json.dumps({"run_id": str(run_id), "status": run_status}),
            )
            return

        await asyncio.sleep(STREAM_POLL_SECONDS)
        elapsed += STREAM_POLL_SECONDS


@router.get("/runs/{run_id}/stream")
def stream_run(
    run_id: UUID,
    session: SessionDep,
    current_user: StreamUserDep,
) -> StreamingResponse:
    _load_owned_run(session, run_id, current_user.id)
    return StreamingResponse(
        _stream_run_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

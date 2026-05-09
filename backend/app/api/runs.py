"""Runs endpoints + SSE stream — implemented in A-PR3 / A-PR4."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import col, select

from app.api.deps import CurrentUserDep, SessionDep
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


# TODO (A-PR4): GET /runs/{id}/stream  → text/event-stream (SSE)
# SSE event shape is locked in app/schemas/events.py — pair with C on Day 3.

TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


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

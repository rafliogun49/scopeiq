"""Projects endpoints — implemented in A-PR3."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import col, delete, select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.chat import ChatMessage
from app.models.chunk import Chunk
from app.models.project import Project
from app.models.run import Run, RunEvent
from app.schemas.projects import (
    LastRunSummary,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithLastRun,
)
from app.schemas.runs import ReportResponse

router = APIRouter()


def _load_owned_project(session: SessionDep, project_id: UUID, user_id: UUID) -> Project:
    project = session.get(Project, project_id)
    if project is None or project.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(session: SessionDep, current_user: CurrentUserDep) -> list[Project]:
    return list(
        session.exec(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(col(Project.created_at).desc())
        ).all()
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> Project:
    project = Project(
        user_id=current_user.id,
        name=body.name,
        idea=body.idea,
        known_competitors=body.known_competitors,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectWithLastRun)
def get_project(
    project_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ProjectWithLastRun:
    project = _load_owned_project(session, project_id, current_user.id)
    last_run = session.exec(
        select(Run)
        .where(Run.project_id == project.id)
        .order_by(col(Run.created_at).desc())
        .limit(1)
    ).first()
    return ProjectWithLastRun(
        **ProjectResponse.model_validate(project).model_dump(),
        last_run=LastRunSummary.model_validate(last_run) if last_run else None,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    body: ProjectUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> Project:
    project = _load_owned_project(session, project_id, current_user.id)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}/report", response_model=ReportResponse)
def get_project_report(
    project_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ReportResponse:
    _load_owned_project(session, project_id, current_user.id)
    run = session.exec(
        select(Run)
        .where(Run.project_id == project_id, Run.status == "completed", Run.report_md.isnot(None))
        .order_by(col(Run.created_at).desc())
        .limit(1)
    ).first()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No report available")
    return ReportResponse(id=run.id, project_id=run.project_id, report_md=run.report_md, created_at=run.created_at)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_project(
    project_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> Response:
    project = _load_owned_project(session, project_id, current_user.id)
    run_ids = list(session.exec(select(Run.id).where(Run.project_id == project.id)).all())
    if run_ids:
        session.exec(delete(RunEvent).where(col(RunEvent.run_id).in_(run_ids)))
        session.exec(delete(Chunk).where(col(Chunk.run_id).in_(run_ids)))
        session.exec(delete(Run).where(col(Run.project_id) == project.id))
    session.exec(delete(ChatMessage).where(col(ChatMessage.project_id) == project.id))
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

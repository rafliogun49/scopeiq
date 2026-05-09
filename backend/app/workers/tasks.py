"""Celery tasks — real research pipeline (A-PR4)."""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.models.project import Project
from app.models.run import Run, RunEvent
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="run_research")
def run_research_task(self, run_id: str) -> dict:
    """
    Main research pipeline task.
    Orchestrator → Scraper handoff via the openai-agents SDK (or stub in tests),
    then hand the RawDocs off to B's index_chunks.
    """
    # Imported here so test fixtures' `monkeypatch.setattr(tasks_module, ...)`
    # picks up the right symbols and to avoid module-load cycles.
    from app.agents.runner import run_orchestrator
    from app.rag.index import index_chunks
    from app.workers.run_events import run_id_var

    run_uuid = UUID(run_id)
    with Session(engine) as session:
        run = session.get(Run, run_uuid)
        if run is None:
            return {"run_id": run_id, "status": "not_found"}
        try:
            run.status = "running"
            run.started_at = datetime.now(UTC)
            session.add(run)
            session.commit()

            project = session.get(Project, run.project_id)
            if project is None:
                raise RuntimeError(f"Project {run.project_id} not found for run {run_uuid}")

            session.add(
                RunEvent(
                    run_id=run_uuid,
                    type="plan",
                    agent="orchestrator",
                    payload={
                        "idea": project.idea,
                        "competitors": list(project.known_competitors or []),
                    },
                )
            )
            session.commit()

            run_id_var.set(run_uuid)
            docs = asyncio.run(run_orchestrator(run_uuid, project))

            try:
                indexed = asyncio.run(index_chunks(run_uuid, docs))
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="log",
                        agent="orchestrator",
                        payload={"indexed_chunks": indexed},
                    )
                )
                session.commit()
            except NotImplementedError:
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="log",
                        agent="orchestrator",
                        payload={
                            "warning": "indexing pending B-PR1",
                            "raw_docs": len(docs),
                        },
                    )
                )
                session.commit()

            run.status = "completed"
            run.finished_at = datetime.now(UTC)
            session.add(run)
            session.commit()
            return {"run_id": run_id, "status": "completed"}
        except Exception as exc:
            session.rollback()
            run = session.get(Run, run_uuid)
            if run is not None:
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="error",
                        agent="orchestrator",
                        payload={"message": str(exc)},
                    )
                )
                run.status = "failed"
                run.error = str(exc)
                run.finished_at = datetime.now(UTC)
                session.add(run)
                session.commit()
            return {"run_id": run_id, "status": "failed"}

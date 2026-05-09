"""Celery tasks — stub expanded in A-PR3 and A-PR4."""
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.models.run import Run, RunEvent
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="run_research")
def run_research_task(self, run_id: str) -> dict:
    """
    Main research pipeline task.
    A-PR3: pending -> running, emits 3 placeholder RunEvents, -> completed.
    A-PR4: boots Orchestrator -> Scraper -> Social -> Synthesizer.
    """
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

            for event in (
                RunEvent(run_id=run_uuid, type="plan", payload={"stub": True}),
                RunEvent(
                    run_id=run_uuid,
                    type="agent_started",
                    agent="orchestrator",
                    payload={"stub": True},
                ),
                RunEvent(
                    run_id=run_uuid,
                    type="agent_finished",
                    agent="orchestrator",
                    payload={"stub": True},
                ),
            ):
                session.add(event)
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
                run.status = "failed"
                run.error = str(exc)
                run.finished_at = datetime.now(UTC)
                session.add(run)
                session.commit()
            return {"run_id": run_id, "status": "failed"}

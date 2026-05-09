"""Celery tasks — stub expanded in A-PR3 and A-PR4."""

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="run_research")
def run_research_task(self, run_id: str) -> dict:
    """
    Main research pipeline task.
    A-PR3: sets run status running → completed (stub).
    A-PR4: boots Orchestrator → Scraper → Social → Synthesizer.
    """
    # TODO (A-PR3): update Run.status to running, then completed
    # TODO (A-PR4): boot orchestrator agent, emit RunEvents, call index_chunks
    raise NotImplementedError(f"run_research_task not implemented — run_id={run_id}")

"""Celery tasks — real research pipeline (A-PR4)."""

from __future__ import annotations

import asyncio
import re
import time
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.core.observability import get_client
from app.models.project import Project
from app.models.run import Run, RunEvent
from app.workers.budget import BudgetExceeded, RunBudget, budget_var
from app.workers.celery_app import celery_app


def _run_with_tpm_retry(fn, max_attempts: int = 3):
    """Call fn(); on OpenAI 429 TPM errors, wait the retry-after time and retry."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            msg = str(exc)
            match = re.search(r"try again in (\d+(?:\.\d+)?)s", msg, re.IGNORECASE)
            if match and attempt < max_attempts - 1:
                wait = float(match.group(1)) + 3  # 3s buffer
                time.sleep(wait)
            else:
                raise


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

        # Initialise a fresh per-run budget and bind it to this async context.
        budget = RunBudget.from_settings()
        budget_var.set(budget)

        # Create a Langfuse span for this run. Using start_observation (not
        # start_as_current_observation) so no OTEL context is attached — avoids
        # context-propagation interference with asyncio.run() and tests.
        lf = get_client()
        lf_span = lf.start_observation(
            as_type="agent",
            name="research_run",
            metadata={"run_id": run_id},
        )

        try:
            print(f"[DEBUG] task starting, budget max_input={budget.max_input_tokens}")
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
            # Emit the active budget caps so the frontend can display them.
            session.add(
                RunEvent(
                    run_id=run_uuid,
                    type="log",
                    agent="orchestrator",
                    payload={"caps": budget.caps_snapshot()},
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

            # ── Social agent: scrape HN / Reddit / StackExchange ─────────────
            session.add(
                RunEvent(run_id=run_uuid, type="agent_started", agent="social", payload={})
            )
            session.commit()
            competitors = list(project.known_competitors or [])
            social_query = project.idea + (
                " " + " ".join(f'"{c}"' for c in competitors) if competitors else ""
            )
            try:
                from app.agents.social import run_social
                social_text = asyncio.run(run_social(social_query, run_id=str(run_uuid)))
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="agent_finished",
                        agent="social",
                        payload={"chars": len(social_text)},
                    )
                )
            except Exception as exc:
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="log",
                        agent="social",
                        payload={"warning": str(exc)[:300]},
                    )
                )
            session.commit()

            # ── Synthesizer agent: generate 4-section report via gpt-4o ──────
            session.add(
                RunEvent(run_id=run_uuid, type="agent_started", agent="synthesizer", payload={})
            )
            session.commit()
            try:
                from app.agents.synthesizer import run_synthesizer
                report_md = _run_with_tpm_retry(
                    lambda: asyncio.run(run_synthesizer(run_id=str(run_uuid), idea=project.idea))
                )
                run.report_md = report_md
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="agent_finished",
                        agent="synthesizer",
                        payload={"words": len(report_md.split())},
                    )
                )
            except Exception as exc:
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="log",
                        agent="synthesizer",
                        payload={"warning": str(exc)[:300]},
                    )
                )
            session.commit()

            run.status = "completed"
            run.finished_at = datetime.now(UTC)
            run.token_input = budget.input_tokens
            run.token_output = budget.output_tokens
            run.cost_usd = budget.cost_usd
            lf_span.update(
                metadata={
                    "status": "completed",
                    "tokens_in": budget.input_tokens,
                    "tokens_out": budget.output_tokens,
                    "cost_usd": round(budget.cost_usd, 6),
                }
            )
            session.add(run)
            session.commit()
            lf_span.end()
            return {"run_id": run_id, "status": "completed"}

        except BudgetExceeded as exc:
            print(f"[DEBUG] BudgetExceeded caught: {exc}")
            session.rollback()
            run = session.get(Run, run_uuid)
            if run is not None:
                session.add(
                    RunEvent(
                        run_id=run_uuid,
                        type="error",
                        agent="orchestrator",
                        payload={"reason": "budget_exceeded", "cap": exc.reason},
                    )
                )
                run.status = "failed"
                run.error = str(exc)
                run.finished_at = datetime.now(UTC)
                # Persist partial counters so the UI can show what was consumed.
                run.token_input = budget.input_tokens
                run.token_output = budget.output_tokens
                run.cost_usd = budget.cost_usd
                lf_span.update(
                    metadata={
                        "status": "failed",
                        "reason": "budget_exceeded",
                        "cap": exc.reason,
                        "tokens_in": budget.input_tokens,
                        "tokens_out": budget.output_tokens,
                    }
                )
                session.add(run)
                session.commit()
            lf_span.end()
            return {"run_id": run_id, "status": "failed"}

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
                run.token_input = budget.input_tokens
                run.token_output = budget.output_tokens
                run.cost_usd = budget.cost_usd
                lf_span.update(metadata={"status": "failed", "error": str(exc)[:500]})
                session.add(run)
                session.commit()
            lf_span.end()
            return {"run_id": run_id, "status": "failed"}

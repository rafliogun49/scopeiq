"""Celery tasks — real research pipeline (A-PR4)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.core.observability import get_client
from app.models.project import Project
from app.models.run import Run, RunEvent
from app.workers.budget import BudgetExceeded, RunBudget, budget_var
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

            # Build a markdown report from the scraped docs.
            if docs:
                from collections import defaultdict

                by_competitor: dict[str, list] = defaultdict(list)
                for d in docs:
                    by_competitor[d.competitor].append(d)
                sections = ["# Competitive Research Report\n"]
                for competitor, comp_docs in by_competitor.items():
                    sections.append(f"## {competitor}\n")
                    for doc in comp_docs[:3]:
                        sections.append(
                            f"**Source:** {doc.url}  \n**Type:** {doc.source_type}\n\n{doc.text[:1200]}\n"
                        )
                run.report_md = "\n---\n\n".join(sections)

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

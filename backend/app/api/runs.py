"""Runs endpoints + SSE stream — implemented in A-PR3 / A-PR4."""
from fastapi import APIRouter

router = APIRouter()


# TODO (A-PR3): POST /projects/{id}/runs, GET /runs/{id}, POST /runs/{id}/cancel
# TODO (A-PR4): GET /runs/{id}/stream  → text/event-stream (SSE)
# SSE event shape is locked in app/schemas/events.py — pair with C on Day 3.
# See PRD §15 Runs section for full spec.

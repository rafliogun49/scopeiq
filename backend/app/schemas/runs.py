from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    status: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    report_md: str | None = None
    cost_usd: float
    token_input: int
    token_output: int
    error: str | None = None
    created_at: datetime


class RunCreateResponse(BaseModel):
    run_id: UUID
    status: str


class RunCancelResponse(BaseModel):
    status: str


class RunEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    timestamp: datetime
    type: str
    agent: str | None = None
    payload: dict[str, Any]

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Run(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    status: str = "pending"  # pending | running | completed | failed | cancelled
    started_at: datetime | None = None
    finished_at: datetime | None = None
    report_md: str | None = None
    cost_usd: float = 0.0
    token_input: int = 0
    token_output: int = 0
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunEvent(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(foreign_key="run.id", index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: str  # plan | agent_started | tool_called | agent_finished | error | log
    agent: str | None = None
    payload: dict = Field(default={}, sa_column=Column(JSONB))

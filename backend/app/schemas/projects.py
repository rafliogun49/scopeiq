from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    idea: str = Field(min_length=1)
    known_competitors: list[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    archived: bool | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    idea: str
    known_competitors: list[str]
    archived: bool
    created_at: datetime


class LastRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    created_at: datetime
    finished_at: datetime | None = None


class ProjectWithLastRun(ProjectResponse):
    last_run: LastRunSummary | None = None

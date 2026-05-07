from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    name: str
    idea: str
    known_competitors: list[str] = Field(default=[], sa_column=Column(JSONB))
    archived: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

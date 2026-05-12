from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ChatMessage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    role: str  # user | assistant
    content: str
    citations: list[dict] = Field(default=[], sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

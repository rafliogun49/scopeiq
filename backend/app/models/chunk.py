from datetime import UTC, datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(foreign_key="run.id", index=True)
    source_url: str
    source_type: str
    competitor: str | None = None
    text: str
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

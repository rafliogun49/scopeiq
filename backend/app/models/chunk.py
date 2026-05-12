from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

# TODO (B-PR1): uncomment pgvector column after running `alembic upgrade head`
# from pgvector.sqlalchemy import Vector
# from sqlalchemy import Column


class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(foreign_key="run.id", index=True)
    source_url: str
    source_type: str  # landing | pricing | review_snippet | hn | stackexchange | community
    competitor: str | None = None
    text: str
    # embedding: list[float] = Field(sa_column=Column(Vector(1536)))  # uncomment in B-PR1
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

"""merge member A and B migrations

Revision ID: 9b52b52ce19a
Revises: 5c65bc26dc74
Create Date: 2026-05-17 20:47:24.759909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '9b52b52ce19a'
down_revision: Union[str, None] = '5c65bc26dc74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""merge member A and B migrations

Revision ID: 5c65bc26dc74
Revises: 0dd2f4ddba50, a5a9e876b36e
Create Date: 2026-05-17 20:46:44.697886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '5c65bc26dc74'
down_revision: Union[str, None] = ('0dd2f4ddba50', 'a5a9e876b36e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

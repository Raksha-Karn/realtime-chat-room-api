"""add message media fields

Revision ID: 74a8b9f0f4c1
Revises: 1f0054ed0799
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "74a8b9f0f4c1"
down_revision: Union[str, Sequence[str], None] = "1f0054ed0799"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("message_type", sa.String(length=20), nullable=False, server_default="text"))
    op.add_column("messages", sa.Column("media_url", sa.Text(), nullable=True))
    op.add_column("messages", sa.Column("media_name", sa.String(length=255), nullable=True))
    op.alter_column("messages", "message_type", server_default=None)


def downgrade() -> None:
    op.drop_column("messages", "media_name")
    op.drop_column("messages", "media_url")
    op.drop_column("messages", "message_type")

"""create system events table

Revision ID: 5e7d8c9a0b1c
Revises: 6f2a9b1c3d4e
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "5e7d8c9a0b1c"
down_revision: Union[str, Sequence[str], None] = "6f2a9b1c3d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "system_events" in inspector.get_table_names():
        return

    op.create_table(
        "system_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=True),
        sa.Column("severity", sa.String(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_system_events_event_type",
        "system_events",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "system_events" not in inspector.get_table_names():
        return

    op.drop_index("ix_system_events_event_type", table_name="system_events")
    op.drop_table("system_events")

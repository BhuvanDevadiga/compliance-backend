"""create usage counters table

Revision ID: 4b1c2d3e4f5a
Revises: 5e7d8c9a0b1c
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "4b1c2d3e4f5a"
down_revision: Union[str, Sequence[str], None] = "5e7d8c9a0b1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "usage_counters" in inspector.get_table_names():
        return

    op.create_table(
        "usage_counters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("period_type", sa.String(), nullable=False),
        sa.Column("period_key", sa.String(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "period_type", "period_key"),
    )
    op.create_index(
        "ix_usage_counters_tenant_id",
        "usage_counters",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "usage_counters" not in inspector.get_table_names():
        return

    op.drop_index("ix_usage_counters_tenant_id", table_name="usage_counters")
    op.drop_table("usage_counters")

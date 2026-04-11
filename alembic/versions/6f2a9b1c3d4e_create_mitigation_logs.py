"""create mitigation logs table

Revision ID: 6f2a9b1c3d4e
Revises: 71472938e6eb
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "6f2a9b1c3d4e"
down_revision: Union[str, Sequence[str], None] = "71472938e6eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "mitigation_logs" in inspector.get_table_names():
        return

    op.create_table(
        "mitigation_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("prediction", sa.String(), nullable=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("ml_probability", sa.Float(), nullable=True),
        sa.Column("hybrid_score", sa.Float(), nullable=True),
        sa.Column("rule_score", sa.Float(), nullable=True),
        sa.Column("actual_escalated", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
    )
    op.create_index(
        "ix_mitigation_logs_tenant_id",
        "mitigation_logs",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_mitigation_logs_timestamp",
        "mitigation_logs",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "mitigation_logs" not in inspector.get_table_names():
        return

    op.drop_index("ix_mitigation_logs_timestamp", table_name="mitigation_logs")
    op.drop_index("ix_mitigation_logs_tenant_id", table_name="mitigation_logs")
    op.drop_table("mitigation_logs")

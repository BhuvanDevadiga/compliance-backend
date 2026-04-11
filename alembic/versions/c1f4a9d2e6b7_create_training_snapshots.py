"""create training_snapshots table

Revision ID: c1f4a9d2e6b7
Revises: b3d1e6f8c2a9
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1f4a9d2e6b7"
down_revision: Union[str, Sequence[str], None] = "b3d1e6f8c2a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "training_snapshots"

    if not inspector.has_table(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=True),
            sa.Column("velocity", sa.Float(), nullable=True),
            sa.Column("stability", sa.Float(), nullable=True),
            sa.Column("bias", sa.Float(), nullable=True),
            sa.Column("forecast_peak", sa.Float(), nullable=True),
            sa.Column("forecast_accuracy", sa.Float(), nullable=True),
            sa.Column("adaptive_threshold", sa.Float(), nullable=True),
            sa.Column("volatility", sa.Float(), nullable=True),
            sa.Column("avg_strategy_confidence", sa.Float(), nullable=True),
            sa.Column("long_term_success_ratio", sa.Float(), nullable=True),
            sa.Column("short_term_success_ratio", sa.Float(), nullable=True),
            sa.Column("escalated", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_training_snapshots_tenant_id"),
            table_name,
            ["tenant_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "training_snapshots"

    if inspector.has_table(table_name):
        index_names = {idx["name"] for idx in inspector.get_indexes(table_name)}
        tenant_idx = op.f("ix_training_snapshots_tenant_id")
        if tenant_idx in index_names:
            op.drop_index(tenant_idx, table_name=table_name)
        op.drop_table(table_name)

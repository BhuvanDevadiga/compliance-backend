"""create decision_snapshots table

Revision ID: f4b7a2d1c9e0
Revises: e2f1c4b8a9d0
Create Date: 2026-03-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4b7a2d1c9e0"
down_revision: Union[str, Sequence[str], None] = "e2f1c4b8a9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "decision_snapshots"

    if not inspector.has_table(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=True),
            sa.Column("risk_level", sa.String(), nullable=True),
            sa.Column("context", sa.String(), nullable=True),
            sa.Column("strategy_stats_json", sa.Text(), nullable=True),
            sa.Column("selected_strategy", sa.String(), nullable=True),
            sa.Column("regret", sa.Float(), nullable=True),
            sa.Column("random_seed", sa.String(), nullable=True),
            sa.Column("engine_version", sa.String(), nullable=True),
            sa.Column("previous_hash", sa.String(), nullable=True),
            sa.Column("current_hash", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_decision_snapshots_tenant_id"),
            table_name,
            ["tenant_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "decision_snapshots"

    if inspector.has_table(table_name):
        index_names = {idx["name"] for idx in inspector.get_indexes(table_name)}
        tenant_idx = op.f("ix_decision_snapshots_tenant_id")
        if tenant_idx in index_names:
            op.drop_index(tenant_idx, table_name=table_name)
        op.drop_table(table_name)

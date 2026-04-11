"""tenant isolated mitigation memory

Revision ID: 035737fd3a05
Revises: 9f3c1d7a2b10
Create Date: 2026-02-24 10:32:34.072993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '035737fd3a05'
down_revision: Union[str, Sequence[str], None] = '9f3c1d7a2b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    strategy_table = "mitigation_strategy_performance"
    if inspector.has_table(strategy_table):
        strategy_indexes = {idx["name"] for idx in inspector.get_indexes(strategy_table)}
        strategy_idx = op.f("ix_mitigation_strategy_performance_strategy")
        tenant_idx = op.f("ix_mitigation_strategy_performance_tenant_id")
        if strategy_idx in strategy_indexes:
            op.drop_index(strategy_idx, table_name=strategy_table)
        if tenant_idx in strategy_indexes:
            op.drop_index(tenant_idx, table_name=strategy_table)
        op.drop_table(strategy_table)

    policy_table = "tenant_policy"
    if inspector.has_table(policy_table):
        policy_indexes = {idx["name"] for idx in inspector.get_indexes(policy_table)}
        policy_idx = op.f("ix_tenant_policy_tenant_id")
        if policy_idx in policy_indexes:
            op.drop_index(policy_idx, table_name=policy_table)
        op.drop_table(policy_table)

    forecast_table = "forecast_evaluation"
    if inspector.has_table(forecast_table):
        forecast_indexes = {idx["name"] for idx in inspector.get_indexes(forecast_table)}
        forecast_idx = op.f("ix_forecast_evaluation_created_at")
        if forecast_idx in forecast_indexes:
            op.drop_index(forecast_idx, table_name=forecast_table)

    mitigation_table = "mitigation_memory"
    if inspector.has_table(mitigation_table):
        columns = {col["name"] for col in inspector.get_columns(mitigation_table)}
        if "tenant_id" not in columns:
            op.add_column(
                mitigation_table,
                sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    mitigation_table = "mitigation_memory"
    if inspector.has_table(mitigation_table):
        columns = {col["name"] for col in inspector.get_columns(mitigation_table)}
        if "tenant_id" in columns:
            op.drop_column(mitigation_table, "tenant_id")

    forecast_table = "forecast_evaluation"
    if inspector.has_table(forecast_table):
        forecast_indexes = {idx["name"] for idx in inspector.get_indexes(forecast_table)}
        forecast_idx = op.f("ix_forecast_evaluation_created_at")
        if forecast_idx not in forecast_indexes:
            op.create_index(forecast_idx, forecast_table, ["created_at"], unique=False)

    policy_table = "tenant_policy"
    if not inspector.has_table(policy_table):
        op.create_table(
            policy_table,
            sa.Column("tenant_id", sa.VARCHAR(), nullable=False),
            sa.Column("policy_name", sa.VARCHAR(), nullable=False),
            sa.Column("rerason_snapshot", sqlite.JSON(), nullable=True),
            sa.Column("updated_at", sa.DATETIME(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.PrimaryKeyConstraint("tenant_id"),
        )
    policy_indexes = {idx["name"] for idx in inspector.get_indexes(policy_table)}
    policy_idx = op.f("ix_tenant_policy_tenant_id")
    if policy_idx not in policy_indexes:
        op.create_index(policy_idx, policy_table, ["tenant_id"], unique=False)

    strategy_table = "mitigation_strategy_performance"
    if not inspector.has_table(strategy_table):
        op.create_table(
            strategy_table,
            sa.Column("id", sa.INTEGER(), nullable=False),
            sa.Column("tenant_id", sa.VARCHAR(), nullable=True),
            sa.Column("strategy", sa.VARCHAR(), nullable=True),
            sa.Column("success_score", sa.FLOAT(), nullable=True),
            sa.Column("failure_score", sa.FLOAT(), nullable=True),
            sa.Column("confidence", sa.FLOAT(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    strategy_indexes = {idx["name"] for idx in inspector.get_indexes(strategy_table)}
    tenant_idx = op.f("ix_mitigation_strategy_performance_tenant_id")
    strategy_idx = op.f("ix_mitigation_strategy_performance_strategy")
    if tenant_idx not in strategy_indexes:
        op.create_index(tenant_idx, strategy_table, ["tenant_id"], unique=False)
    if strategy_idx not in strategy_indexes:
        op.create_index(strategy_idx, strategy_table, ["strategy"], unique=False)

"""create mitigation strategy performance table

Revision ID: 9f3c1d7a2b10
Revises: 3533043a76e2
Create Date: 2026-02-19 13:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3c1d7a2b10"
down_revision: Union[str, Sequence[str], None] = "3533043a76e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy_performance"

    if table_name not in inspector.get_table_names():
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=True),
            sa.Column("strategy", sa.String(), nullable=True),
            sa.Column("success_score", sa.Float(), nullable=True),
            sa.Column("failure_score", sa.Float(), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_mitigation_strategy_performance_tenant_id"),
            table_name,
            ["tenant_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_mitigation_strategy_performance_strategy"),
            table_name,
            ["strategy"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy_performance"

    if table_name in inspector.get_table_names():
        index_names = {idx["name"] for idx in inspector.get_indexes(table_name)}
        tenant_idx = op.f("ix_mitigation_strategy_performance_tenant_id")
        strategy_idx = op.f("ix_mitigation_strategy_performance_strategy")

        if tenant_idx in index_names:
            op.drop_index(tenant_idx, table_name=table_name)
        if strategy_idx in index_names:
            op.drop_index(strategy_idx, table_name=table_name)
        op.drop_table(table_name)

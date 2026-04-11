"""add short term metrics to mitigation_strategy_performance

Revision ID: b3d1e6f8c2a9
Revises: a7c2e3f4b1c0
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b3d1e6f8c2a9"
down_revision: Union[str, Sequence[str], None] = "a7c2e3f4b1c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy_performance"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        with op.batch_alter_table(table_name) as batch_op:
            if "short_term_success" not in columns:
                batch_op.add_column(
                    sa.Column("short_term_success", sa.Float(), nullable=True, server_default=sa.text("0.0"))
                )
            if "short_term_failure" not in columns:
                batch_op.add_column(
                    sa.Column("short_term_failure", sa.Float(), nullable=True, server_default=sa.text("0.0"))
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy_performance"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        with op.batch_alter_table(table_name) as batch_op:
            if "short_term_failure" in columns:
                batch_op.drop_column("short_term_failure")
            if "short_term_success" in columns:
                batch_op.drop_column("short_term_success")

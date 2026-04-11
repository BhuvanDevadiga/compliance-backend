"""add confidence to strategy_performance

Revision ID: a7c2e3f4b1c0
Revises: 035737fd3a05
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7c2e3f4b1c0"
down_revision: Union[str, Sequence[str], None] = "035737fd3a05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "strategy_performance"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        if "confidence" not in columns:
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.add_column(
                    sa.Column("confidence", sa.Float(), nullable=True, server_default=sa.text("0.5"))
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "strategy_performance"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        if "confidence" in columns:
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.drop_column("confidence")

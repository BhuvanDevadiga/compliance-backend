"""add active fields to mitigation_strategy

Revision ID: e2f1c4b8a9d0
Revises: c1f4a9d2e6b7
Create Date: 2026-03-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2f1c4b8a9d0"
down_revision: Union[str, Sequence[str], None] = "c1f4a9d2e6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        added_is_active = False
        with op.batch_alter_table(table_name) as batch_op:
            if "is_active" not in columns:
                batch_op.add_column(
                    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1"))
                )
                added_is_active = True
            if "retired_at" not in columns:
                batch_op.add_column(sa.Column("retired_at", sa.DateTime(), nullable=True))

        if added_is_active or "is_active" in columns:
            op.execute(sa.text("UPDATE mitigation_strategy SET is_active = 1 WHERE is_active IS NULL"))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "mitigation_strategy"

    if inspector.has_table(table_name):
        columns = {col["name"] for col in inspector.get_columns(table_name)}
        with op.batch_alter_table(table_name) as batch_op:
            if "retired_at" in columns:
                batch_op.drop_column("retired_at")
            if "is_active" in columns:
                batch_op.drop_column("is_active")

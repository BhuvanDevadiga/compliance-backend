"""add last_reason to tenant_risk_state

Revision ID: c4b2de71f9ab
Revises: a1c6f9d2b7e3
Create Date: 2026-02-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "c4b2de71f9ab"
down_revision: Union[str, Sequence[str], None] = "8c1d2e3f4a5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("tenant_risk_state")}

    if "last_reason" not in existing_columns:
        with op.batch_alter_table("tenant_risk_state") as batch_op:
            batch_op.add_column(sa.Column("last_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("tenant_risk_state")}

    if "last_reason" in existing_columns:
        with op.batch_alter_table("tenant_risk_state") as batch_op:
            batch_op.drop_column("last_reason")

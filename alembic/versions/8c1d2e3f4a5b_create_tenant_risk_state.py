"""create tenant risk state table

Revision ID: 8c1d2e3f4a5b
Revises: a1c6f9d2b7e3
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "8c1d2e3f4a5b"
down_revision: Union[str, Sequence[str], None] = "a1c6f9d2b7e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "tenant_risk_state" in inspector.get_table_names():
        return

    op.create_table(
        "tenant_risk_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(), nullable=True),
        sa.Column("last_escalation_reason", sa.String(), nullable=True),
        sa.Column("last_reason", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("quarantined", sa.Boolean(), nullable=True),
        sa.Column("quarantine_reason", sa.String(), nullable=True),
        sa.Column("quarantined_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_tenant_risk_state_tenant_id",
        "tenant_risk_state",
        ["tenant_id"],
        unique=True,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "tenant_risk_state" not in inspector.get_table_names():
        return

    op.drop_index("ix_tenant_risk_state_tenant_id", table_name="tenant_risk_state")
    op.drop_table("tenant_risk_state")

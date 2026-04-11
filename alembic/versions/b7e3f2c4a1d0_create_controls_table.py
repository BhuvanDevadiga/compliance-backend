"""create controls table

Revision ID: b7e3f2c4a1d0
Revises: a0264eb96a41
Create Date: 2026-04-02 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7e3f2c4a1d0"
down_revision: Union[str, Sequence[str], None] = "a0264eb96a41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "controls",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("framework", sa.String(), nullable=False),
        sa.Column("last_evidence_updated_at", sa.DateTime(), nullable=True),
        sa.Column("owner_last_login", sa.DateTime(), nullable=True),
        sa.Column("historical_failure_rate", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("next_audit_date", sa.DateTime(), nullable=True),
        sa.Column("control_failure_prob", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("control_risk_level", sa.String(length=10), nullable=False, server_default="LOW"),
        sa.Column("control_risk_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_controls_tenant_id"), "controls", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_controls_tenant_id"), table_name="controls")
    op.drop_table("controls")

"""mitigation outcome memory

Revision ID: 71472938e6eb
Revises: dbc2ac2dc2a6
Create Date: 2026-02-17 15:39:48.664527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71472938e6eb'
down_revision: Union[str, Sequence[str], None] = 'dbc2ac2dc2a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create mitigation outcomes table and indexes (idempotent for partial reruns).
    if not inspector.has_table("mitigation_outcomes"):
        op.create_table(
            "mitigation_outcomes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False),
            sa.Column("mitigation_action", sa.String(), nullable=False),
            sa.Column("behavior_improved", sa.Boolean(), nullable=False),
            sa.Column(
                "timestamp",
                sa.DateTime(),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    mitigation_outcome_indexes = {idx["name"] for idx in inspector.get_indexes("mitigation_outcomes")}
    if "ix_mitigation_outcomes_id" not in mitigation_outcome_indexes:
        op.create_index("ix_mitigation_outcomes_id", "mitigation_outcomes", ["id"], unique=False)
    if "ix_mitigation_outcomes_tenant_id" not in mitigation_outcome_indexes:
        op.create_index("ix_mitigation_outcomes_tenant_id", "mitigation_outcomes", ["tenant_id"], unique=False)

    # Keep mitigation_logs id index in sync with model if table exists.
    if inspector.has_table("mitigation_logs"):
        mitigation_log_indexes = {idx["name"] for idx in inspector.get_indexes("mitigation_logs")}
        if "ix_mitigation_logs_id" not in mitigation_log_indexes:
            op.create_index("ix_mitigation_logs_id", "mitigation_logs", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("mitigation_logs"):
        mitigation_log_indexes = {idx["name"] for idx in inspector.get_indexes("mitigation_logs")}
        if "ix_mitigation_logs_id" in mitigation_log_indexes:
            op.drop_index("ix_mitigation_logs_id", table_name="mitigation_logs")

    if inspector.has_table("mitigation_outcomes"):
        mitigation_outcome_indexes = {idx["name"] for idx in inspector.get_indexes("mitigation_outcomes")}
        if "ix_mitigation_outcomes_tenant_id" in mitigation_outcome_indexes:
            op.drop_index("ix_mitigation_outcomes_tenant_id", table_name="mitigation_outcomes")
        if "ix_mitigation_outcomes_id" in mitigation_outcome_indexes:
            op.drop_index("ix_mitigation_outcomes_id", table_name="mitigation_outcomes")
        op.drop_table("mitigation_outcomes")

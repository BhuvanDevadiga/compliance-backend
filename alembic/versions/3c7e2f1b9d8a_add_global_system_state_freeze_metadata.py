"""add global system state freeze metadata

Revision ID: 3c7e2f1b9d8a
Revises: 1abab5650e71
Create Date: 2026-03-20 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3c7e2f1b9d8a"
down_revision: Union[str, Sequence[str], None] = "1abab5650e71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "global_system_state",
        sa.Column("freeze_locked_version", sa.String(), nullable=True),
    )
    op.add_column(
        "global_system_state",
        sa.Column(
            "platform_override_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "global_system_state",
        sa.Column("platform_override_reason", sa.String(), nullable=True),
    )
    op.add_column(
        "global_system_state",
        sa.Column("platform_override_locked_version", sa.String(), nullable=True),
    )
    op.add_column(
        "global_system_state",
        sa.Column("platform_override_activated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("global_system_state", "platform_override_activated_at")
    op.drop_column("global_system_state", "platform_override_locked_version")
    op.drop_column("global_system_state", "platform_override_reason")
    op.drop_column("global_system_state", "platform_override_active")
    op.drop_column("global_system_state", "freeze_locked_version")

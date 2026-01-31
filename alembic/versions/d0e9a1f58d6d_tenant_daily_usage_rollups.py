"""tenant daily usage rollups

Revision ID: d0e9a1f58d6d
Revises: 821b9a17c149
Create Date: 2026-01-26 11:42:41.535143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0e9a1f58d6d'
down_revision: Union[str, Sequence[str], None] = '821b9a17c149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "tenant_usage_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("request_count", sa.Integer(), default=0),
        sa.Column("last_seen", sa.DateTime()),
        sa.UniqueConstraint(
            "tenant_id",
            "path",
            "method",
            "usage_date",
            name="uq_tenant_usage_daily",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass

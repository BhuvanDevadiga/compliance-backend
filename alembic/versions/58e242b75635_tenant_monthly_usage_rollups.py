"""tenant monthly usage rollups

Revision ID: 58e242b75635
Revises: 25d04afa88dd
Create Date: 2026-01-27 12:43:10.994828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58e242b75635'
down_revision: Union[str, Sequence[str], None] = '25d04afa88dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "tenant_usage_monthly",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=False),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("method", sa.String, nullable=False),
        sa.Column("request_count", sa.Integer, default=0),
        sa.Column("last_seen", sa.DateTime),
        sa.UniqueConstraint(
            "tenant_id", "year", "month", "path", "method",
            name="uq_tenant_monthly_usage"
        ),
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass

"""tenant usage counters

Revision ID: 821b9a17c149
Revises: 
Create Date: 2026-01-24 11:05:54.596569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '821b9a17c149'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_usage",
        sa.Column("id", sa.Integer, primary_key=True),

        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("method", sa.String, nullable=False),

        sa.Column("usage_date", sa.Date, nullable=False),

        sa.Column(
            "request_count",
            sa.Integer,
            nullable=False,
            server_default="1",
        ),

        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),

        sa.UniqueConstraint(
            "tenant_id",
            "path",
            "method",
            "usage_date",
            name="uq_tenant_usage_day",
        ),
    )

def downgrade():
    op.drop_table("tenant_usage")

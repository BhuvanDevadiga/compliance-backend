"""tenant quotas

Revision ID: 25d04afa88dd
Revises: d0e9a1f58d6d
Create Date: 2026-01-26 12:50:35.803410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25d04afa88dd'
down_revision: Union[str, Sequence[str], None] = 'd0e9a1f58d6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "tenant_quotas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False, unique=True),
        sa.Column("plan", sa.String, nullable=False),
        sa.Column("daily_limit", sa.Integer, nullable=False),
        sa.Column("monthly_limit", sa.Integer, nullable=False),
        sa.Column("enforce_hard_limit", sa.Boolean, nullable=False),
    )


def downgrade():
    op.drop_table("tenant_quotas")
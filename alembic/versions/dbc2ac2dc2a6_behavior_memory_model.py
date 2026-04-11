"""behavior memory model

Revision ID: dbc2ac2dc2a6
Revises: c4b2de71f9ab
Create Date: 2026-02-16 15:07:57.958498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'dbc2ac2dc2a6'
down_revision: Union[str, Sequence[str], None] = 'c4b2de71f9ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "behavior_memory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("behavior_score", sa.Float(), nullable=False),
        sa.Column("volatility", sa.String(), nullable=False),
        sa.Column("classification", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_behavior_memory_id", "behavior_memory", ["id"])
    op.create_index("ix_behavior_memory_tenant_id", "behavior_memory", ["tenant_id"])



def downgrade():
    op.drop_index("ix_behavior_memory_tenant_id", table_name="behavior_memory")
    op.drop_index("ix_behavior_memory_id", table_name="behavior_memory")
    op.drop_table("behavior_memory")

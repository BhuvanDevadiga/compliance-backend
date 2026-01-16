"""create risk_assessments table

Revision ID: b64dd63fdc8c
Revises: 
Create Date: 2026-01-12 19:08:33.385996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b64dd63fdc8c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('company_size', sa.Integer(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('has_gst', sa.Boolean(), nullable=False),
        sa.Column('has_pan', sa.Boolean(), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
    )
    op.create_index(
        'ix_risk_assessments_id',
        'risk_assessments',
        ['id']
    )


def downgrade() -> None:
    op.drop_index('ix_risk_assessments_id', table_name='risk_assessments')
    op.drop_table('risk_assessments')


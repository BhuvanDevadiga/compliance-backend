"""add fingerprint and error_type to request audit logs

Revision ID: a1c6f9d2b7e3
Revises: 58e242b75635
Create Date: 2026-02-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "a1c6f9d2b7e3"
down_revision: Union[str, Sequence[str], None] = "7b9c1a2d3e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("request_audit_logs")}

    with op.batch_alter_table("request_audit_logs") as batch_op:
        if "fingerprint" not in existing_columns:
            batch_op.add_column(sa.Column("fingerprint", sa.String(), nullable=True))
        if "error_type" not in existing_columns:
            batch_op.add_column(sa.Column("error_type", sa.String(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("request_audit_logs")}

    with op.batch_alter_table("request_audit_logs") as batch_op:
        if "error_type" in existing_columns:
            batch_op.drop_column("error_type")
        if "fingerprint" in existing_columns:
            batch_op.drop_column("fingerprint")

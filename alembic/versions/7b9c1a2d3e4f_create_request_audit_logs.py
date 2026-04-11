"""create request audit logs table

Revision ID: 7b9c1a2d3e4f
Revises: 58e242b75635
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "7b9c1a2d3e4f"
down_revision: Union[str, Sequence[str], None] = "58e242b75635"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "request_audit_logs" in inspector.get_table_names():
        return

    op.create_table(
        "request_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("ruleset_version", sa.String(length=36), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("api_key_hash", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_hash", sa.Text(), nullable=True),
        sa.Column("payload_hash", sa.String(), nullable=True),
        sa.Column("response_size", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(), nullable=True),
        sa.Column("error_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_request_audit_logs_request_id",
        "request_audit_logs",
        ["request_id"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "request_audit_logs" not in inspector.get_table_names():
        return

    op.drop_index("ix_request_audit_logs_request_id", table_name="request_audit_logs")
    op.drop_table("request_audit_logs")

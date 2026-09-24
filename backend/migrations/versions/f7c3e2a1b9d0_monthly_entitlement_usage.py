"""add monthly entitlement usage ledger

Revision ID: f7c3e2a1b9d0
Revises: d2fd5b60754a
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7c3e2a1b9d0"
down_revision: Union[str, Sequence[str], None] = "d2fd5b60754a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usage_ledger",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("metric", sa.String(length=50), nullable=False),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "metric",
            "period_start",
            name="uq_usage_user_metric_period",
        ),
    )
    op.create_index("ix_usage_ledger_user_id", "usage_ledger", ["user_id"])
    op.create_index("ix_usage_ledger_metric", "usage_ledger", ["metric"])
    op.create_index("ix_usage_ledger_period_start", "usage_ledger", ["period_start"])


def downgrade() -> None:
    op.drop_index("ix_usage_ledger_period_start", table_name="usage_ledger")
    op.drop_index("ix_usage_ledger_metric", table_name="usage_ledger")
    op.drop_index("ix_usage_ledger_user_id", table_name="usage_ledger")
    op.drop_table("usage_ledger")

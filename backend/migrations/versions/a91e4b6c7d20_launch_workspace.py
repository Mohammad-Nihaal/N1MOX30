"""add launch workspace communications and clips

Revision ID: a91e4b6c7d20
Revises: f7c3e2a1b9d0
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a91e4b6c7d20"
down_revision: Union[str, Sequence[str], None] = "f7c3e2a1b9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "communication_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("sender", sa.String(length=255), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("auto_reply_enabled", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_messages_user_id", "communication_messages", ["user_id"])

    op.create_table(
        "clip_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("requested_formats", sa.JSON(), nullable=False),
        sa.Column("pipeline", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clip_jobs_user_id", "clip_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_clip_jobs_user_id", table_name="clip_jobs")
    op.drop_table("clip_jobs")
    op.drop_index("ix_communication_messages_user_id", table_name="communication_messages")
    op.drop_table("communication_messages")

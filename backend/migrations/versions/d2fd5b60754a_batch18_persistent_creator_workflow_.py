"""batch18 persistent creator workflow state

Revision ID: d2fd5b60754a
Revises: 4bbd7aab6d3e
Create Date: 2026-09-19 23:30:48.179843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2fd5b60754a'
down_revision: Union[str, Sequence[str], None] = '4bbd7aab6d3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass



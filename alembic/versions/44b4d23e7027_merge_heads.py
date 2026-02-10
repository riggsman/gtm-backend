"""merge heads

Revision ID: 44b4d23e7027
Revises: 3b14a0c510fa
Create Date: 2026-01-31 00:35:38.247141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44b4d23e7027'
down_revision: Union[str, Sequence[str], None] = '3b14a0c510fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

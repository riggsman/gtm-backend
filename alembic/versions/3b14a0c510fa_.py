"""empty message

Revision ID: 3b14a0c510fa
Revises: 5af58a26bf4d, migrate_pages_to_individual_tables
Create Date: 2026-01-31 00:26:31.354538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b14a0c510fa'
down_revision: Union[str, Sequence[str], None] = ('5af58a26bf4d', 'migrate_pages_to_individual_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

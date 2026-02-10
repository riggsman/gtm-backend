"""empty message

Revision ID: 096a91541866
Revises: 0834a0a8f521, add_about_content, add_html_content_pages
Create Date: 2026-01-26 20:48:49.056866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '096a91541866'
down_revision: Union[str, Sequence[str], None] = ('0834a0a8f521', 'add_about_content', 'add_html_content_pages')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

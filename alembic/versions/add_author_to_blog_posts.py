"""Add author field to blog posts

Revision ID: add_author_blog
Revises: 604df26e5335
Create Date: 2026-01-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_author_blog'
down_revision: Union[str, None] = '604df26e5335'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add author column to blog_posts table."""
    op.add_column('blog_posts', sa.Column('author', sa.String(255), nullable=True))


def downgrade() -> None:
    """Remove author column from blog_posts table."""
    op.drop_column('blog_posts', 'author')

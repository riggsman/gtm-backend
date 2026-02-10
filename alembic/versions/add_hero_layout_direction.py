"""Add hero_layout_direction field

Revision ID: add_hero_layout_direction
Revises: a1ecad7b11f7
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_hero_layout_direction'
down_revision = 'add_author_blog'
branch_labels = None
depends_on = None


def upgrade():
    # Add hero_layout_direction column to site_settings table
    op.add_column('site_settings', sa.Column('hero_layout_direction', sa.String(length=10), server_default='left', nullable=True))


def downgrade():
    # Remove hero_layout_direction column from site_settings table
    op.drop_column('site_settings', 'hero_layout_direction')

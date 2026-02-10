"""Add statistics section fields to site_settings

Revision ID: add_statistics_section
Revises: add_partner_section
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_statistics_section'
down_revision = 'add_partner_section'
branch_labels = None
depends_on = None


def upgrade():
    # Add statistics section fields to site_settings table
    op.add_column('site_settings', sa.Column('statistics_section_visible', sa.Integer(), server_default='1', nullable=True))
    op.add_column('site_settings', sa.Column('statistics_section_title', sa.String(length=255), server_default='OUR NUMBERS', nullable=True))


def downgrade():
    # Remove statistics section fields from site_settings table
    op.drop_column('site_settings', 'statistics_section_title')
    op.drop_column('site_settings', 'statistics_section_visible')

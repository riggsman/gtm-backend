"""Add partner section fields to site_settings

Revision ID: add_partner_section
Revises: add_hero_layout_direction
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_partner_section'
down_revision = 'add_hero_layout_direction'
branch_labels = None
depends_on = None


def upgrade():
    # Add partner section fields to site_settings table
    op.add_column('site_settings', sa.Column('partner_section_visible', sa.Integer(), server_default='1', nullable=True))
    op.add_column('site_settings', sa.Column('partner_section_title', sa.String(length=255), server_default='Become a Partner', nullable=True))
    op.add_column('site_settings', sa.Column('partner_section_content', sa.Text(), nullable=True))
    op.add_column('site_settings', sa.Column('partner_section_button_text', sa.String(length=255), server_default='Partner With Us', nullable=True))
    op.add_column('site_settings', sa.Column('partner_section_button_url', sa.String(length=255), server_default='contact.html', nullable=True))


def downgrade():
    # Remove partner section fields from site_settings table
    op.drop_column('site_settings', 'partner_section_button_url')
    op.drop_column('site_settings', 'partner_section_button_text')
    op.drop_column('site_settings', 'partner_section_content')
    op.drop_column('site_settings', 'partner_section_title')
    op.drop_column('site_settings', 'partner_section_visible')

"""Add SMTP configuration fields to site_settings

Revision ID: add_smtp_config
Revises: add_statistics_section
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_smtp_config'
down_revision = 'add_statistics_section'
branch_labels = None
depends_on = None


def upgrade():
    # Add SMTP configuration fields to site_settings table
    op.add_column('site_settings', sa.Column('smtp_sender_email', sa.String(length=255), nullable=True))
    op.add_column('site_settings', sa.Column('smtp_sender_password', sa.String(length=255), nullable=True))
    op.add_column('site_settings', sa.Column('smtp_host', sa.String(length=255), server_default='smtp.gmail.com', nullable=True))
    op.add_column('site_settings', sa.Column('smtp_port', sa.Integer(), server_default='587', nullable=True))


def downgrade():
    # Remove SMTP configuration fields from site_settings table
    op.drop_column('site_settings', 'smtp_port')
    op.drop_column('site_settings', 'smtp_host')
    op.drop_column('site_settings', 'smtp_sender_password')
    op.drop_column('site_settings', 'smtp_sender_email')

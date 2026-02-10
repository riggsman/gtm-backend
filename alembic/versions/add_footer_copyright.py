"""Add footer_copyright field to site_settings

Revision ID: add_footer_copyright
Revises: add_statistics_section
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_footer_copyright'
down_revision = 'add_statistics_section'
branch_labels = None
depends_on = None


def upgrade():
    # Add footer_copyright field to site_settings table (only if it doesn't exist)
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('site_settings')]
    
    if 'footer_copyright' not in columns:
        op.add_column('site_settings', sa.Column('footer_copyright', sa.Text(), server_default='Powered By IT Centre Glorious Church Copyright @ 2023', nullable=True))


def downgrade():
    # Remove footer_copyright field from site_settings table
    op.drop_column('site_settings', 'footer_copyright')

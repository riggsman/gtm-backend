"""Add html_content field to pages table

Revision ID: add_html_content_pages
Revises: add_footer_copyright
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_html_content_pages'
down_revision = 'add_footer_copyright'
branch_labels = None
depends_on = None


def upgrade():
    # Add html_content field to pages table (only if it doesn't exist)
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('pages')]
    
    if 'html_content' not in columns:
        op.add_column('pages', sa.Column('html_content', sa.Text(), nullable=True))


def downgrade():
    # Remove html_content field from pages table
    op.drop_column('pages', 'html_content')

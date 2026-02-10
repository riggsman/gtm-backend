"""add about_content table

Revision ID: add_about_content
Revises: add_testimonials_table
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_about_content'
down_revision = 'add_documents'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'about_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='About Us'),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('mission', sa.Text(), nullable=True),
        sa.Column('vision', sa.Text(), nullable=True),
        sa.Column('values', sa.Text(), nullable=True),
        sa.Column('history', sa.Text(), nullable=True),
        sa.Column('leadership', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_about_content_id'), 'about_content', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_about_content_id'), table_name='about_content')
    op.drop_table('about_content')

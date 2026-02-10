"""Add documents table

Revision ID: add_documents
Revises: add_testimonials
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_documents'
down_revision = 'add_testimonials'
branch_labels = None
depends_on = None


def upgrade():
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_downloadable', sa.Integer(), server_default='1', nullable=True),
        sa.Column('is_viewable', sa.Integer(), server_default='1', nullable=True),
        sa.Column('prevent_screenshots', sa.Integer(), server_default='0', nullable=True),
        sa.Column('is_visible', sa.Integer(), server_default='1', nullable=True),
        sa.Column('order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)


def downgrade():
    # Drop documents table
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

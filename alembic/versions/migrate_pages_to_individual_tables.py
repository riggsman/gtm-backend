"""Migrate pages table to individual page tables

Revision ID: migrate_pages_to_individual_tables
Revises: add_html_content_pages
Create Date: 2024-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect


# revision identifiers, used by Alembic.
revision = 'migrate_pages_to_individual_tables'
down_revision = 'add_html_content_pages'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if pages table exists
    tables = inspector.get_table_names()
    if 'pages' not in tables:
        # If pages table doesn't exist, just create the new tables
        create_all_page_tables()
        return
    
    # Get all pages data before creating new tables
    pages_data = conn.execute(text("SELECT * FROM pages")).fetchall()
    pages_columns = [col['name'] for col in inspector.get_columns('pages')]
    
    # Create all new page tables
    create_all_page_tables()
    
    # Update about table to include new fields
    update_about_table()
    
    # Migrate data from pages table to new tables
    migrate_pages_data(conn, pages_data, pages_columns)
    
    # Drop the pages table
    op.drop_table('pages')


def create_all_page_tables():
    """Create all individual page tables"""
    
    # Home Page
    op.create_table('home_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Home'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('news_section_title', sa.String(length=255), nullable=True, server_default='News'),
        sa.Column('news_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('partner_section_title', sa.String(length=255), nullable=True, server_default='Become a Partner'),
        sa.Column('partner_section_content', sa.Text(), nullable=True),
        sa.Column('partner_section_button_text', sa.String(length=255), nullable=True, server_default='Partner With Us'),
        sa.Column('partner_section_button_url', sa.String(length=255), nullable=True, server_default='contact.html'),
        sa.Column('partner_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('events_section_title', sa.String(length=255), nullable=True, server_default='OUR EVENTS'),
        sa.Column('events_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('statistics_section_title', sa.String(length=255), nullable=True, server_default='OUR NUMBERS'),
        sa.Column('statistics_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('partners_faith_section_title', sa.String(length=255), nullable=True, server_default='PARTNERS IN FAITH'),
        sa.Column('partners_faith_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('testimonials_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('testimonial1_title', sa.String(length=255), nullable=True),
        sa.Column('testimonial1_content', sa.Text(), nullable=True),
        sa.Column('testimonial1_author', sa.String(length=255), nullable=True),
        sa.Column('testimonial1_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('testimonial2_title', sa.String(length=255), nullable=True),
        sa.Column('testimonial2_content', sa.Text(), nullable=True),
        sa.Column('testimonial2_author', sa.String(length=255), nullable=True),
        sa.Column('testimonial2_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('latest_news_section_title', sa.String(length=255), nullable=True, server_default='Latest News'),
        sa.Column('latest_news_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('newsletter_section_title', sa.String(length=255), nullable=True, server_default='Newsletter'),
        sa.Column('newsletter_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Contact Page
    op.create_table('contact_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Contact'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Contact Us'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Get in Touch'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('contact_info_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('contact_form_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('contact_partner_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('contact_partner_title', sa.String(length=255), nullable=True),
        sa.Column('contact_partner_content', sa.Text(), nullable=True),
        sa.Column('contact_partner_button_text', sa.String(length=255), nullable=True),
        sa.Column('contact_partner_button_url', sa.String(length=255), nullable=True),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Blog Page
    op.create_table('blog_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Blog'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Blog'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Latest News & Updates'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('blog_content_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('blog_sidebar_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('blog_recent_posts_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('blog_categories_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('blog_newsletter_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Gallery Page
    op.create_table('gallery_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Gallery'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Gallery'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Our Church in Pictures'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('gallery_filter_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('gallery_content_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Branches Page
    op.create_table('branches_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Branches'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Branches'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Our Regional Offices'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('branches_content_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Departments Page
    op.create_table('departments_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Departments'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Departments'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Our Organizational Structure'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('departments_content_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Events Page
    op.create_table('events_page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True, server_default='Events'),
        sa.Column('page_header_title', sa.String(length=255), nullable=True, server_default='Our Events'),
        sa.Column('page_header_subtitle', sa.String(length=255), nullable=True, server_default='Stay updated with our upcoming events and activities'),
        sa.Column('page_header_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('events_content_section_visible', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def update_about_table():
    """Update about table to include new common page fields"""
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if about table exists
    tables = inspector.get_table_names()
    if 'about' not in tables:
        return
    
    columns = [col['name'] for col in inspector.get_columns('about')]
    
    # Add new fields if they don't exist
    new_fields = [
        ('title', sa.String(length=255), 'About'),
        ('page_header_title', sa.String(length=255), 'About Us'),
        ('page_header_subtitle', sa.String(length=255), None),
        ('page_header_visible', sa.Integer(), 1),
        ('history_visible', sa.Integer(), 1),
        ('mission_visible', sa.Integer(), 1),
        ('vision_visible', sa.Integer(), 1),
        ('values_visible', sa.Integer(), 1),
        ('institutions_visible', sa.Integer(), 1),
        ('content1', sa.Text(), None),
        ('content1_visible', sa.Integer(), 1),
        ('content1_label', sa.String(length=255), 'Content 1'),
        ('content2', sa.Text(), None),
        ('content2_visible', sa.Integer(), 1),
        ('content2_label', sa.String(length=255), 'Content 2'),
        ('content3', sa.Text(), None),
        ('content3_visible', sa.Integer(), 1),
        ('content3_label', sa.String(length=255), 'Content 3'),
        ('is_published', sa.Integer(), 0),
        ('published_at', sa.DateTime(timezone=True), None),
        ('created_at', sa.DateTime(timezone=True), None),
        ('created_by', sa.Integer(), None),
        ('updated_by', sa.Integer(), None),
    ]
    
    for field_name, field_type, default_value in new_fields:
        if field_name not in columns:
            if default_value is not None:
                if isinstance(default_value, str):
                    op.add_column('about', sa.Column(field_name, field_type, server_default=default_value, nullable=True))
                else:
                    op.add_column('about', sa.Column(field_name, field_type, server_default=str(default_value), nullable=True))
            else:
                op.add_column('about', sa.Column(field_name, field_type, nullable=True))


def migrate_pages_data(conn, pages_data, pages_columns):
    """Migrate data from pages table to individual page tables"""
    
    # Map page_name to table name
    page_mapping = {
        'home': 'home_page',
        'index': 'home_page',
        'about': 'about',
        'contact': 'contact_page',
        'blog': 'blog_page',
        'gallery': 'gallery_page',
        'branches': 'branches_page',
        'departments': 'departments_page',
        'events': 'events_page',
    }
    
    # Get column index mapping
    col_index = {col: i for i, col in enumerate(pages_columns)}
    
    for page_row in pages_data:
        # Get page_name from row
        if 'page_name' not in col_index:
            continue
        
        page_name = page_row[col_index['page_name']]
        normalized_name = page_name.lower() if page_name else None
        
        if not normalized_name or normalized_name not in page_mapping:
            continue
        
        target_table = page_mapping[normalized_name]
        
        # Build insert statement based on target table
        if target_table == 'home_page':
            migrate_home_page(conn, page_row, col_index, target_table)
        elif target_table == 'contact_page':
            migrate_contact_page(conn, page_row, col_index, target_table)
        elif target_table == 'blog_page':
            migrate_blog_page(conn, page_row, col_index, target_table)
        elif target_table == 'gallery_page':
            migrate_gallery_page(conn, page_row, col_index, target_table)
        elif target_table == 'branches_page':
            migrate_branches_page(conn, page_row, col_index, target_table)
        elif target_table == 'departments_page':
            migrate_departments_page(conn, page_row, col_index, target_table)
        elif target_table == 'events_page':
            migrate_events_page(conn, page_row, col_index, target_table)
        elif target_table == 'about':
            migrate_about_page(conn, page_row, col_index)


def get_value(row, col_index, col_name, default=None):
    """Get value from row by column name"""
    if col_name in col_index:
        return row[col_index[col_name]]
    return default


def migrate_home_page(conn, row, col_index, table_name):
    """Migrate data to home_page table"""
    # Check if record already exists
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return  # Already migrated
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Home'),
        'page_header_title': get_value(row, col_index, 'page_header_title'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'news_section_title': get_value(row, col_index, 'news_section_title', 'News'),
        'news_section_visible': get_value(row, col_index, 'news_section_visible', 1),
        'partner_section_title': get_value(row, col_index, 'partner_section_title', 'Become a Partner'),
        'partner_section_content': get_value(row, col_index, 'partner_section_content'),
        'partner_section_button_text': get_value(row, col_index, 'partner_section_button_text', 'Partner With Us'),
        'partner_section_button_url': get_value(row, col_index, 'partner_section_button_url', 'contact.html'),
        'partner_section_visible': get_value(row, col_index, 'partner_section_visible', 1),
        'events_section_title': get_value(row, col_index, 'events_section_title', 'OUR EVENTS'),
        'events_section_visible': get_value(row, col_index, 'events_section_visible', 1),
        'statistics_section_title': get_value(row, col_index, 'statistics_section_title', 'OUR NUMBERS'),
        'statistics_section_visible': get_value(row, col_index, 'statistics_section_visible', 1),
        'partners_faith_section_title': get_value(row, col_index, 'partners_faith_section_title', 'PARTNERS IN FAITH'),
        'partners_faith_section_visible': get_value(row, col_index, 'partners_faith_section_visible', 1),
        'testimonials_section_visible': get_value(row, col_index, 'testimonials_section_visible', 1),
        'testimonial1_title': get_value(row, col_index, 'testimonial1_title'),
        'testimonial1_content': get_value(row, col_index, 'testimonial1_content'),
        'testimonial1_author': get_value(row, col_index, 'testimonial1_author'),
        'testimonial1_visible': get_value(row, col_index, 'testimonial1_visible', 1),
        'testimonial2_title': get_value(row, col_index, 'testimonial2_title'),
        'testimonial2_content': get_value(row, col_index, 'testimonial2_content'),
        'testimonial2_author': get_value(row, col_index, 'testimonial2_author'),
        'testimonial2_visible': get_value(row, col_index, 'testimonial2_visible', 1),
        'latest_news_section_title': get_value(row, col_index, 'latest_news_section_title', 'Latest News'),
        'latest_news_section_visible': get_value(row, col_index, 'latest_news_section_visible', 1),
        'newsletter_section_title': get_value(row, col_index, 'newsletter_section_title', 'Newsletter'),
        'newsletter_section_visible': get_value(row, col_index, 'newsletter_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    # Build and execute insert
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_contact_page(conn, row, col_index, table_name):
    """Migrate data to contact_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Contact'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Contact Us'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Get in Touch'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'contact_info_section_visible': get_value(row, col_index, 'contact_info_section_visible', 1),
        'contact_form_section_visible': get_value(row, col_index, 'contact_form_section_visible', 1),
        'contact_partner_section_visible': get_value(row, col_index, 'contact_partner_section_visible', 1),
        'contact_partner_title': get_value(row, col_index, 'contact_partner_title'),
        'contact_partner_content': get_value(row, col_index, 'contact_partner_content'),
        'contact_partner_button_text': get_value(row, col_index, 'contact_partner_button_text'),
        'contact_partner_button_url': get_value(row, col_index, 'contact_partner_button_url'),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_blog_page(conn, row, col_index, table_name):
    """Migrate data to blog_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Blog'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Blog'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Latest News & Updates'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'blog_content_section_visible': get_value(row, col_index, 'blog_content_section_visible', 1),
        'blog_sidebar_section_visible': get_value(row, col_index, 'blog_sidebar_section_visible', 1),
        'blog_recent_posts_section_visible': get_value(row, col_index, 'blog_recent_posts_section_visible', 1),
        'blog_categories_section_visible': get_value(row, col_index, 'blog_categories_section_visible', 1),
        'blog_newsletter_section_visible': get_value(row, col_index, 'blog_newsletter_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_gallery_page(conn, row, col_index, table_name):
    """Migrate data to gallery_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Gallery'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Gallery'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Our Church in Pictures'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'gallery_filter_section_visible': get_value(row, col_index, 'gallery_filter_section_visible', 1),
        'gallery_content_section_visible': get_value(row, col_index, 'gallery_content_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_branches_page(conn, row, col_index, table_name):
    """Migrate data to branches_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Branches'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Branches'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Our Regional Offices'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'branches_content_section_visible': get_value(row, col_index, 'branches_content_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_departments_page(conn, row, col_index, table_name):
    """Migrate data to departments_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Departments'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Departments'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Our Organizational Structure'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'departments_content_section_visible': get_value(row, col_index, 'departments_content_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_events_page(conn, row, col_index, table_name):
    """Migrate data to events_page table"""
    existing = conn.execute(text(f"SELECT id FROM {table_name} LIMIT 1")).fetchone()
    if existing:
        return
    
    fields = {
        'title': get_value(row, col_index, 'title', 'Events'),
        'page_header_title': get_value(row, col_index, 'page_header_title', 'Our Events'),
        'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle', 'Stay updated with our upcoming events and activities'),
        'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
        'events_content_section_visible': get_value(row, col_index, 'events_content_section_visible', 1),
        'is_published': get_value(row, col_index, 'is_published', 0),
        'published_at': get_value(row, col_index, 'published_at'),
        'created_at': get_value(row, col_index, 'created_at'),
        'updated_at': get_value(row, col_index, 'updated_at'),
        'created_by': get_value(row, col_index, 'created_by'),
        'updated_by': get_value(row, col_index, 'updated_by'),
    }
    
    cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
    vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
    conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"))


def migrate_about_page(conn, row, col_index):
    """Migrate data to about table"""
    existing = conn.execute(text("SELECT id FROM about LIMIT 1")).fetchone()
    if existing:
        # Update existing about record
        update_fields = []
        if 'title' in col_index and row[col_index['title']]:
            update_fields.append(f"title = '{row[col_index['title']]}'")
        if 'page_header_title' in col_index and row[col_index['page_header_title']]:
            update_fields.append(f"page_header_title = '{row[col_index['page_header_title']]}'")
        if 'page_header_subtitle' in col_index and row[col_index['page_header_subtitle']]:
            update_fields.append(f"page_header_subtitle = '{row[col_index['page_header_subtitle']]}'")
        if 'page_header_visible' in col_index:
            update_fields.append(f"page_header_visible = {row[col_index['page_header_visible']] or 1}")
        # Add other fields as needed
        if update_fields:
            conn.execute(text(f"UPDATE about SET {', '.join(update_fields)} WHERE id = {existing[0]}"))
    else:
        # Insert new about record
        fields = {
            'title': get_value(row, col_index, 'title', 'About'),
            'page_header_title': get_value(row, col_index, 'page_header_title', 'About Us'),
            'page_header_subtitle': get_value(row, col_index, 'page_header_subtitle'),
            'page_header_visible': get_value(row, col_index, 'page_header_visible', 1),
            'history': get_value(row, col_index, 'history'),
            'history_visible': get_value(row, col_index, 'history_visible', 1),
            'mission': get_value(row, col_index, 'mission'),
            'mission_visible': get_value(row, col_index, 'mission_visible', 1),
            'vision': get_value(row, col_index, 'vision'),
            'vision_visible': get_value(row, col_index, 'vision_visible', 1),
            'values': get_value(row, col_index, 'values'),
            'values_visible': get_value(row, col_index, 'values_visible', 1),
            'institutions': get_value(row, col_index, 'institutions'),
            'institutions_visible': get_value(row, col_index, 'institutions_visible', 1),
            'content1': get_value(row, col_index, 'content1'),
            'content1_visible': get_value(row, col_index, 'content1_visible', 1),
            'content1_label': get_value(row, col_index, 'content1_label', 'Content 1'),
            'content2': get_value(row, col_index, 'content2'),
            'content2_visible': get_value(row, col_index, 'content2_visible', 1),
            'content2_label': get_value(row, col_index, 'content2_label', 'Content 2'),
            'content3': get_value(row, col_index, 'content3'),
            'content3_visible': get_value(row, col_index, 'content3_visible', 1),
            'content3_label': get_value(row, col_index, 'content3_label', 'Content 3'),
            'is_published': get_value(row, col_index, 'is_published', 0),
            'published_at': get_value(row, col_index, 'published_at'),
            'created_at': get_value(row, col_index, 'created_at'),
            'updated_at': get_value(row, col_index, 'updated_at'),
            'created_by': get_value(row, col_index, 'created_by'),
            'updated_by': get_value(row, col_index, 'updated_by'),
        }
        
        cols = ', '.join([k for k in fields.keys() if fields[k] is not None])
        vals = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) if v is not None else 'NULL' for k, v in fields.items() if fields[k] is not None])
        conn.execute(text(f"INSERT INTO about ({cols}) VALUES ({vals})"))


def downgrade():
    """Revert the migration - recreate pages table and migrate data back"""
    # Note: This is a complex downgrade that would require recreating the pages table
    # and merging data from all individual tables back. For now, we'll just drop the new tables.
    
    # Drop all new page tables
    op.drop_table('events_page')
    op.drop_table('departments_page')
    op.drop_table('branches_page')
    op.drop_table('gallery_page')
    op.drop_table('blog_page')
    op.drop_table('contact_page')
    op.drop_table('home_page')
    
    # Note: We don't recreate the pages table in downgrade as it would be too complex
    # The user would need to manually restore from backup if needed

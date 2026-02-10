from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.sql import func
from database import Base

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(255))  # Icon class name
    image_url = Column(String(255))  # Department image URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(255))
    category = Column(String(255))  # Optional category for blog posts
    author = Column(String(255))  # Optional author name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    time = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(255), nullable=False)  # events, worship, community, institutions
    image_url = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Testimonial(Base):
    __tablename__ = "testimonials"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Testimonial title/heading
    content = Column(Text, nullable=False)  # Testimonial content/quote
    author = Column(String(255), nullable=False)  # Author name
    order = Column(Integer, default=0)  # For ordering testimonials
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Document title/name
    file_url = Column(String(500), nullable=False)  # File path/URL
    file_type = Column(String(50))  # File extension/type (pdf, docx, etc.)
    file_size = Column(Integer)  # File size in bytes
    description = Column(Text)  # Optional description
    is_downloadable = Column(Integer, default=1)  # 1 = downloadable, 0 = not downloadable
    is_viewable = Column(Integer, default=1)  # 1 = viewable, 0 = not viewable
    prevent_screenshots = Column(Integer, default=0)  # 1 = prevent screenshots, 0 = allow
    is_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    order = Column(Integer, default=0)  # For ordering documents
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class About(Base):
    __tablename__ = "about"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="About")
    # Page Header
    page_header_title = Column(String(255), default="About Us")
    page_header_subtitle = Column(String(255))
    page_header_visible = Column(Integer, default=1)
    # About page content
    history = Column(Text)
    history_visible = Column(Integer, default=1)
    mission = Column(Text)
    mission_visible = Column(Integer, default=1)
    vision = Column(Text)
    vision_visible = Column(Integer, default=1)
    values = Column(Text)  # JSON string or comma-separated values
    values_visible = Column(Integer, default=1)
    institutions = Column(Text)
    institutions_visible = Column(Integer, default=1)
    # Additional flexible content fields
    content1 = Column(Text)
    content1_visible = Column(Integer, default=1)
    content1_label = Column(String(255), default="Content 1")
    content2 = Column(Text)
    content2_visible = Column(Integer, default=1)
    content2_label = Column(String(255), default="Content 2")
    content3 = Column(Text)
    content3_visible = Column(Integer, default=1)
    content3_label = Column(String(255), default="Content 3")
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class NavigationItem(Base):
    __tablename__ = "navigation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    order = Column(Integer, default=0)  # For ordering menu items
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SiteSettings(Base):
    __tablename__ = "site_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(255), default="Throne of Glory Ministry International")  # Navbar brand/title
    tagline = Column(String(255))  # Tagline below site name
    # Typography settings - stored as JSON strings or individual fields
    site_name_font_family = Column(String(255), default="inherit")
    site_name_font_size = Column(String(255), default="1.25rem")
    site_name_font_weight = Column(String(255), default="bold")
    site_name_color = Column(String(255), default="inherit")
    tagline_font_family = Column(String(255), default="inherit")
    tagline_font_size = Column(String(255), default="0.7rem")
    tagline_font_weight = Column(String(255), default="normal")
    tagline_color = Column(String(255), default="rgba(255,255,255,0.5)")
    # Theme colors - CSS custom properties
    theme_primary = Column(String(255), default="#0d6efd")
    theme_secondary = Column(String(255), default="#6c757d")
    theme_success = Column(String(255), default="#198754")
    theme_danger = Column(String(255), default="#dc3545")
    theme_warning = Column(String(255), default="#ffc107")
    theme_info = Column(String(255), default="#0dcaf0")
    theme_light = Column(String(255), default="#f8f9fa")
    theme_dark = Column(String(255), default="#212529")
    # Hero section content
    hero_title = Column(Text, default="Throne of Glory Ministry International")
    hero_subtitle = Column(Text, default="Glorious Church")
    hero_button1_text = Column(String(255), default="Fellowship with Us")
    hero_button1_url = Column(String(255), default="branches.html")
    hero_button1_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_button2_text = Column(String(255), default="Contact Us")
    hero_button2_url = Column(String(255), default="contact.html")
    hero_button2_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_image_url = Column(String(255))  # Optional hero image
    hero_image_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_background_image_url = Column(String(255))  # Optional background image
    hero_background_image_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_layout_direction = Column(String(10), default="left")  # "left" = text left/image right, "right" = image left/text right
    # Email notification settings
    admin_emails = Column(Text)  # Comma-separated list of admin emails to receive notifications
    # SMTP server configuration
    smtp_sender_email = Column(String(255))  # SENDER_EMAIL / SMTP_USERNAME
    smtp_sender_password = Column(String(255))  # SENDER_PASSWORD / SMTP_PASSWORD
    smtp_host = Column(String(255), default="smtp.gmail.com")  # SMTP_HOST / SMTP_SERVER
    smtp_port = Column(Integer, default=587)  # SMTP_PORT
    # Admin panel settings
    admin_panel_title = Column(String(255), default="TGMI")  # Admin panel title
    # Feature flags - control visibility of features in admin panel (1 = enabled, 0 = disabled)
    feature_dashboard = Column(Integer, default=1)
    feature_blog = Column(Integer, default=1)
    feature_branches = Column(Integer, default=1)
    feature_departments = Column(Integer, default=1)
    feature_events = Column(Integer, default=1)
    feature_gallery = Column(Integer, default=1)
    feature_contact = Column(Integer, default=1)
    feature_pages = Column(Integer, default=1)
    feature_about = Column(Integer, default=1)
    feature_navigation = Column(Integer, default=1)
    feature_users = Column(Integer, default=1)
    feature_settings = Column(Integer, default=1)
    # Social media links
    social_facebook_url = Column(String(255))
    social_twitter_url = Column(String(255))
    social_instagram_url = Column(String(255))
    social_youtube_url = Column(String(255))
    social_linkedin_url = Column(String(255))
    social_section_visible = Column(Integer, default=0)  # 1 = visible, 0 = hidden
    # Quick links
    quick_links_section_visible = Column(Integer, default=0)  # 1 = visible, 0 = hidden
    quick_links_pages = Column(Text)  # JSON array of page names to display
    # Contact information
    contact_email = Column(String(255))
    contact_phone = Column(String(255))
    contact_address = Column(Text)
    contact_office_hours = Column(Text)
    contact_section_visible = Column(Integer, default=0)  # 1 = visible, 0 = hidden
    # Partner section (Become a Partner)
    partner_section_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    partner_section_title = Column(String(255), default="Become a Partner")
    partner_section_content = Column(Text)
    partner_section_button_text = Column(String(255), default="Partner With Us")
    partner_section_button_url = Column(String(255), default="contact.html")
    # Statistics section (Our Numbers)
    statistics_section_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    statistics_section_title = Column(String(255), default="OUR NUMBERS")
    # Footer settings
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Page models - each page type has its own table
# Common fields for all page types
class HomePage(Base):
    __tablename__ = "home_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Home")  # Page title
    # Page Header
    page_header_title = Column(String(255))
    page_header_subtitle = Column(String(255))
    page_header_visible = Column(Integer, default=1)
    # Home page specific sections
    news_section_title = Column(String(255), default="News")
    news_section_visible = Column(Integer, default=1)
    partner_section_title = Column(String(255), default="Become a Partner")
    partner_section_content = Column(Text)
    partner_section_button_text = Column(String(255), default="Partner With Us")
    partner_section_button_url = Column(String(255), default="contact.html")
    partner_section_visible = Column(Integer, default=1)
    events_section_title = Column(String(255), default="OUR EVENTS")
    events_section_visible = Column(Integer, default=1)
    statistics_section_title = Column(String(255), default="OUR NUMBERS")
    statistics_section_visible = Column(Integer, default=1)
    partners_faith_section_title = Column(String(255), default="PARTNERS IN FAITH")
    partners_faith_section_visible = Column(Integer, default=1)
    testimonials_section_visible = Column(Integer, default=1)
    testimonial1_title = Column(String(255))
    testimonial1_content = Column(Text)
    testimonial1_author = Column(String(255))
    testimonial1_visible = Column(Integer, default=1)
    testimonial2_title = Column(String(255))
    testimonial2_content = Column(Text)
    testimonial2_author = Column(String(255))
    testimonial2_visible = Column(Integer, default=1)
    latest_news_section_title = Column(String(255), default="Latest News")
    latest_news_section_visible = Column(Integer, default=1)
    newsletter_section_title = Column(String(255), default="Newsletter")
    newsletter_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class ContactPage(Base):
    __tablename__ = "contact_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Contact")
    # Page Header
    page_header_title = Column(String(255), default="Contact Us")
    page_header_subtitle = Column(String(255), default="Get in Touch")
    page_header_visible = Column(Integer, default=1)
    # Contact page specific
    contact_info_section_visible = Column(Integer, default=1)
    contact_form_section_visible = Column(Integer, default=1)
    contact_partner_section_visible = Column(Integer, default=1)
    contact_partner_title = Column(String(255))
    contact_partner_content = Column(Text)
    contact_partner_button_text = Column(String(255))
    contact_partner_button_url = Column(String(255))
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class BlogPage(Base):
    __tablename__ = "blog_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Blog")
    # Page Header
    page_header_title = Column(String(255), default="Blog")
    page_header_subtitle = Column(String(255), default="Latest News & Updates")
    page_header_visible = Column(Integer, default=1)
    # Blog page specific
    blog_content_section_visible = Column(Integer, default=1)
    blog_sidebar_section_visible = Column(Integer, default=1)
    blog_recent_posts_section_visible = Column(Integer, default=1)
    blog_categories_section_visible = Column(Integer, default=1)
    blog_newsletter_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class GalleryPage(Base):
    __tablename__ = "gallery_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Gallery")
    # Page Header
    page_header_title = Column(String(255), default="Gallery")
    page_header_subtitle = Column(String(255), default="Our Church in Pictures")
    page_header_visible = Column(Integer, default=1)
    # Gallery page specific
    gallery_filter_section_visible = Column(Integer, default=1)
    gallery_content_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class BranchesPage(Base):
    __tablename__ = "branches_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Branches")
    # Page Header
    page_header_title = Column(String(255), default="Branches")
    page_header_subtitle = Column(String(255), default="Our Regional Offices")
    page_header_visible = Column(Integer, default=1)
    # Branches page specific
    branches_content_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class DepartmentsPage(Base):
    __tablename__ = "departments_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Departments")
    # Page Header
    page_header_title = Column(String(255), default="Departments")
    page_header_subtitle = Column(String(255), default="Our Organizational Structure")
    page_header_visible = Column(Integer, default=1)
    # Departments page specific
    departments_content_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class EventsPage(Base):
    __tablename__ = "events_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Events")
    # Page Header
    page_header_title = Column(String(255), default="Our Events")
    page_header_subtitle = Column(String(255), default="Stay updated with our upcoming events and activities")
    page_header_visible = Column(Integer, default=1)
    # Events page specific
    events_content_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

class DocumentsPage(Base):
    __tablename__ = "documents_page"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Documents")
    # Page Header
    page_header_title = Column(String(255), default="Documents")
    page_header_subtitle = Column(String(255), default="Browse and download our documents")
    page_header_visible = Column(Integer, default=1)
    # Documents page specific
    documents_content_section_visible = Column(Integer, default=1)
    is_published = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

# Update About model to include common fields
# About model already exists, but we need to add common page fields

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False, default="contributor")  # contributor, admin, super_admin
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)  # User ID who created this user

# DEPRECATED: AboutContent model - Use About model instead
# This model is kept for backward compatibility with existing migrations
# All new code should use the About model (about table)
# class AboutContent(Base):
#     __tablename__ = "about_content"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255), default="About Us")
#     content = Column(Text)  # Main content HTML/text
#     mission = Column(Text)  # Mission statement
#     vision = Column(Text)  # Vision statement
#     values = Column(Text)  # Values/Principles
#     history = Column(Text)  # History/Background
#     leadership = Column(Text)  # Leadership information
#     is_published = Column(Integer, default=1)  # 0 = draft, 1 = published
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#     updated_by = Column(Integer)  # User ID who last updated

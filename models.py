from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.sql import func
from database import Base

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)  # Icon class name
    image_url = Column(String)  # Department image URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    time = Column(String)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)  # events, worship, community, institutions
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class About(Base):
    __tablename__ = "about"
    
    id = Column(Integer, primary_key=True, index=True)
    history = Column(Text)
    mission = Column(Text)
    vision = Column(Text)
    values = Column(Text)  # JSON string or comma-separated values
    institutions = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class NavigationItem(Base):
    __tablename__ = "navigation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    url = Column(String, nullable=False)
    order = Column(Integer, default=0)  # For ordering menu items
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SiteSettings(Base):
    __tablename__ = "site_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, default="Glorious Church")  # Navbar brand/title
    tagline = Column(String)  # Tagline below site name
    # Typography settings - stored as JSON strings or individual fields
    site_name_font_family = Column(String, default="inherit")
    site_name_font_size = Column(String, default="1.25rem")
    site_name_font_weight = Column(String, default="bold")
    site_name_color = Column(String, default="inherit")
    tagline_font_family = Column(String, default="inherit")
    tagline_font_size = Column(String, default="0.7rem")
    tagline_font_weight = Column(String, default="normal")
    tagline_color = Column(String, default="rgba(255,255,255,0.5)")
    # Theme colors - CSS custom properties
    theme_primary = Column(String, default="#0d6efd")
    theme_secondary = Column(String, default="#6c757d")
    theme_success = Column(String, default="#198754")
    theme_danger = Column(String, default="#dc3545")
    theme_warning = Column(String, default="#ffc107")
    theme_info = Column(String, default="#0dcaf0")
    theme_light = Column(String, default="#f8f9fa")
    theme_dark = Column(String, default="#212529")
    # Hero section content
    hero_title = Column(Text, default="Welcome To\nThe Presbyterian Church In Cameroon")
    hero_subtitle = Column(Text, default="Grow your faith via our institutions and make a difference in knowing Jesus Christ")
    hero_button1_text = Column(String, default="Live stream CBS Bamenda")
    hero_button1_url = Column(String, default="#")
    hero_button1_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_button2_text = Column(String, default="Live Stream CBS Buea")
    hero_button2_url = Column(String, default="#")
    hero_button2_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_image_url = Column(String)  # Optional hero image
    hero_image_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    hero_background_image_url = Column(String)  # Optional background image
    hero_background_image_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    # Email notification settings
    admin_emails = Column(Text)  # Comma-separated list of admin emails to receive notifications
    # Admin panel settings
    admin_panel_title = Column(String, default="Glorious Church CMS")  # Admin panel title
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Page(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String, nullable=False, unique=True)  # e.g., "about", "home", "branches"
    title = Column(String)  # Page title
    # Page Header (common to all pages)
    page_header_title = Column(String)  # Header title (e.g., "Branches", "Contact Us")
    page_header_subtitle = Column(String)  # Header subtitle (e.g., "Our Regional Offices")
    page_header_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
    # Content fields (similar to About)
    history = Column(Text)
    history_visible = Column(Integer, default=1)  # 1 = visible, 0 = hidden
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
    content1_label = Column(String, default="Content 1")
    content2 = Column(Text)
    content2_visible = Column(Integer, default=1)
    content2_label = Column(String, default="Content 2")
    content3 = Column(Text)
    content3_visible = Column(Integer, default=1)
    content3_label = Column(String, default="Content 3")
    # Home page specific sections
    news_section_title = Column(String, default="News")
    news_section_visible = Column(Integer, default=1)
    partner_section_title = Column(String, default="Become a Partner")
    partner_section_content = Column(Text)
    partner_section_button_text = Column(String, default="Partner With Us")
    partner_section_button_url = Column(String, default="contact.html")
    partner_section_visible = Column(Integer, default=1)
    events_section_title = Column(String, default="OUR EVENTS")
    events_section_visible = Column(Integer, default=1)
    statistics_section_title = Column(String, default="OUR NUMBERS")
    statistics_section_visible = Column(Integer, default=1)
    partners_faith_section_title = Column(String, default="PARTNERS IN FAITH")
    partners_faith_section_visible = Column(Integer, default=1)
    testimonials_section_visible = Column(Integer, default=1)
    testimonial1_title = Column(String)
    testimonial1_content = Column(Text)
    testimonial1_author = Column(String)
    testimonial1_visible = Column(Integer, default=1)
    testimonial2_title = Column(String)
    testimonial2_content = Column(Text)
    testimonial2_author = Column(String)
    testimonial2_visible = Column(Integer, default=1)
    latest_news_section_title = Column(String, default="Latest News")
    latest_news_section_visible = Column(Integer, default=1)
    newsletter_section_title = Column(String, default="Newsletter")
    newsletter_section_visible = Column(Integer, default=1)
    # Gallery page specific
    gallery_filter_section_visible = Column(Integer, default=1)
    gallery_content_section_visible = Column(Integer, default=1)
    # Contact page specific
    contact_info_section_visible = Column(Integer, default=1)
    contact_form_section_visible = Column(Integer, default=1)
    contact_partner_section_visible = Column(Integer, default=1)
    contact_partner_title = Column(String)
    contact_partner_content = Column(Text)
    contact_partner_button_text = Column(String)
    contact_partner_button_url = Column(String)
    # Blog page specific
    blog_content_section_visible = Column(Integer, default=1)
    blog_sidebar_section_visible = Column(Integer, default=1)
    blog_recent_posts_section_visible = Column(Integer, default=1)
    blog_categories_section_visible = Column(Integer, default=1)
    blog_newsletter_section_visible = Column(Integer, default=1)
    # Branches page specific
    branches_content_section_visible = Column(Integer, default=1)
    # Departments page specific
    departments_content_section_visible = Column(Integer, default=1)
    # Events page specific
    events_content_section_visible = Column(Integer, default=1)
    # Branches/Departments/Events pages - use generic content fields
    # Publish status
    is_published = Column(Integer, default=0)  # 0 = draft, 1 = published
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)  # User ID who created/updated
    updated_by = Column(Integer)  # User ID who last updated

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="contributor")  # contributor, admin, super_admin
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)  # User ID who created this user

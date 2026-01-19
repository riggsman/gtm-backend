from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class BranchBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None

class BranchCreate(BranchBase):
    pass

class BranchResponse(BranchBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BlogPostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostResponse(BlogPostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ContactMessageBase(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessageResponse(ContactMessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: date
    time: Optional[str] = None
    location: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GalleryImageBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    image_url: str

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageResponse(GalleryImageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AboutBase(BaseModel):
    history: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[str] = None  # JSON string or comma-separated
    institutions: Optional[str] = None

class AboutCreate(AboutBase):
    pass

class AboutResponse(AboutBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NavigationItemBase(BaseModel):
    label: str
    url: str
    order: int = 0
    is_active: int = 1

class NavigationItemCreate(NavigationItemBase):
    pass

class NavigationItemUpdate(BaseModel):
    label: Optional[str] = None
    url: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[int] = None

class NavigationItemResponse(NavigationItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteSettingsBase(BaseModel):
    site_name: str = "Glorious Church"
    tagline: Optional[str] = None
    site_name_font_family: Optional[str] = "inherit"
    site_name_font_size: Optional[str] = "1.25rem"
    site_name_font_weight: Optional[str] = "bold"
    site_name_color: Optional[str] = "inherit"
    tagline_font_family: Optional[str] = "inherit"
    tagline_font_size: Optional[str] = "0.7rem"
    tagline_font_weight: Optional[str] = "normal"
    tagline_color: Optional[str] = "rgba(255,255,255,0.5)"
    theme_primary: Optional[str] = "#0d6efd"
    theme_secondary: Optional[str] = "#6c757d"
    theme_success: Optional[str] = "#198754"
    theme_danger: Optional[str] = "#dc3545"
    theme_warning: Optional[str] = "#ffc107"
    theme_info: Optional[str] = "#0dcaf0"
    theme_light: Optional[str] = "#f8f9fa"
    theme_dark: Optional[str] = "#212529"
    hero_title: Optional[str] = "Welcome To\nThe Presbyterian Church In Cameroon"
    hero_subtitle: Optional[str] = "Grow your faith via our institutions and make a difference in knowing Jesus Christ"
    hero_button1_text: Optional[str] = "Live stream CBS Bamenda"
    hero_button1_url: Optional[str] = "#"
    hero_button1_visible: Optional[int] = 1
    hero_button2_text: Optional[str] = "Live Stream CBS Buea"
    hero_button2_url: Optional[str] = "#"
    hero_button2_visible: Optional[int] = 1
    hero_image_url: Optional[str] = None
    hero_image_visible: Optional[int] = None
    hero_background_image_url: Optional[str] = None
    hero_background_image_visible: Optional[int] = None
    # Email notification settings
    admin_emails: Optional[str] = None
    # Admin panel settings
    admin_panel_title: Optional[str] = "Glorious Church CMS"
    # Feature flags
    feature_dashboard: Optional[int] = 1
    feature_blog: Optional[int] = 1
    feature_branches: Optional[int] = 1
    feature_departments: Optional[int] = 1
    feature_events: Optional[int] = 1
    feature_gallery: Optional[int] = 1
    feature_contact: Optional[int] = 1
    feature_pages: Optional[int] = 1
    feature_about: Optional[int] = 1
    feature_navigation: Optional[int] = 1
    feature_users: Optional[int] = 1
    feature_settings: Optional[int] = 1

class SiteSettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    tagline: Optional[str] = None
    site_name_font_family: Optional[str] = None
    site_name_font_size: Optional[str] = None
    site_name_font_weight: Optional[str] = None
    site_name_color: Optional[str] = None
    tagline_font_family: Optional[str] = None
    tagline_font_size: Optional[str] = None
    tagline_font_weight: Optional[str] = None
    tagline_color: Optional[str] = None
    theme_primary: Optional[str] = None
    theme_secondary: Optional[str] = None
    theme_success: Optional[str] = None
    theme_danger: Optional[str] = None
    theme_warning: Optional[str] = None
    theme_info: Optional[str] = None
    theme_light: Optional[str] = None
    theme_dark: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_button1_text: Optional[str] = None
    hero_button1_url: Optional[str] = None
    hero_button1_visible: Optional[int] = None
    hero_button2_text: Optional[str] = None
    hero_button2_url: Optional[str] = None
    hero_button2_visible: Optional[int] = None
    hero_image_url: Optional[str] = None
    hero_image_visible: Optional[int] = None
    hero_background_image_url: Optional[str] = None
    hero_background_image_visible: Optional[int] = None
    # Email notification settings
    admin_emails: Optional[str] = None
    # Admin panel settings
    admin_panel_title: Optional[str] = "Glorious Church CMS"

class SiteSettingsResponse(SiteSettingsBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Page schemas
class PageBase(BaseModel):
    page_name: str
    title: Optional[str] = None
    # Page Header (common to all pages)
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = 1
    # Content fields (similar to About)
    history: Optional[str] = None
    history_visible: Optional[int] = 1
    mission: Optional[str] = None
    mission_visible: Optional[int] = 1
    vision: Optional[str] = None
    vision_visible: Optional[int] = 1
    values: Optional[str] = None
    values_visible: Optional[int] = 1
    institutions: Optional[str] = None
    institutions_visible: Optional[int] = 1
    content1: Optional[str] = None
    content1_visible: Optional[int] = 1
    content1_label: Optional[str] = "Content 1"
    content2: Optional[str] = None
    content2_visible: Optional[int] = 1
    content2_label: Optional[str] = "Content 2"
    content3: Optional[str] = None
    content3_visible: Optional[int] = 1
    content3_label: Optional[str] = "Content 3"
    # Home page specific sections
    news_section_title: Optional[str] = "News"
    news_section_visible: Optional[int] = 1
    partner_section_title: Optional[str] = "Become a Partner"
    partner_section_content: Optional[str] = None
    partner_section_button_text: Optional[str] = "Partner With Us"
    partner_section_button_url: Optional[str] = "contact.html"
    partner_section_visible: Optional[int] = 1
    events_section_title: Optional[str] = "OUR EVENTS"
    events_section_visible: Optional[int] = 1
    statistics_section_title: Optional[str] = "OUR NUMBERS"
    statistics_section_visible: Optional[int] = 1
    partners_faith_section_title: Optional[str] = "PARTNERS IN FAITH"
    partners_faith_section_visible: Optional[int] = 1
    testimonials_section_visible: Optional[int] = 1
    testimonial1_title: Optional[str] = None
    testimonial1_content: Optional[str] = None
    testimonial1_author: Optional[str] = None
    testimonial1_visible: Optional[int] = 1
    testimonial2_title: Optional[str] = None
    testimonial2_content: Optional[str] = None
    testimonial2_author: Optional[str] = None
    testimonial2_visible: Optional[int] = 1
    latest_news_section_title: Optional[str] = "Latest News"
    latest_news_section_visible: Optional[int] = 1
    newsletter_section_title: Optional[str] = "Newsletter"
    newsletter_section_visible: Optional[int] = 1
    # Gallery page specific
    gallery_filter_section_visible: Optional[int] = 1
    gallery_content_section_visible: Optional[int] = 1
    # Contact page specific
    contact_info_section_visible: Optional[int] = 1
    contact_form_section_visible: Optional[int] = 1
    contact_partner_section_visible: Optional[int] = 1
    contact_partner_title: Optional[str] = None
    contact_partner_content: Optional[str] = None
    contact_partner_button_text: Optional[str] = None
    contact_partner_button_url: Optional[str] = None
    # Blog page specific
    blog_content_section_visible: Optional[int] = 1
    blog_sidebar_section_visible: Optional[int] = 1
    blog_recent_posts_section_visible: Optional[int] = 1
    blog_categories_section_visible: Optional[int] = 1
    blog_newsletter_section_visible: Optional[int] = 1
    # Branches page specific
    branches_content_section_visible: Optional[int] = 1
    # Departments page specific
    departments_content_section_visible: Optional[int] = 1
    # Events page specific
    events_content_section_visible: Optional[int] = 1

class PageCreate(PageBase):
    is_published: Optional[int] = 0

class PageUpdate(BaseModel):
    title: Optional[str] = None
    # Page Header (common to all pages)
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    # Content fields
    history: Optional[str] = None
    history_visible: Optional[int] = None
    mission: Optional[str] = None
    mission_visible: Optional[int] = None
    vision: Optional[str] = None
    vision_visible: Optional[int] = None
    values: Optional[str] = None
    values_visible: Optional[int] = None
    institutions: Optional[str] = None
    institutions_visible: Optional[int] = None
    content1: Optional[str] = None
    content1_visible: Optional[int] = None
    content1_label: Optional[str] = None
    content2: Optional[str] = None
    content2_visible: Optional[int] = None
    content2_label: Optional[str] = None
    content3: Optional[str] = None
    content3_visible: Optional[int] = None
    content3_label: Optional[str] = None
    # Home page specific sections
    news_section_title: Optional[str] = None
    news_section_visible: Optional[int] = None
    partner_section_title: Optional[str] = None
    partner_section_content: Optional[str] = None
    partner_section_button_text: Optional[str] = None
    partner_section_button_url: Optional[str] = None
    partner_section_visible: Optional[int] = None
    events_section_title: Optional[str] = None
    events_section_visible: Optional[int] = None
    statistics_section_title: Optional[str] = None
    statistics_section_visible: Optional[int] = None
    partners_faith_section_title: Optional[str] = None
    partners_faith_section_visible: Optional[int] = None
    testimonials_section_visible: Optional[int] = None
    testimonial1_title: Optional[str] = None
    testimonial1_content: Optional[str] = None
    testimonial1_author: Optional[str] = None
    testimonial1_visible: Optional[int] = None
    testimonial2_title: Optional[str] = None
    testimonial2_content: Optional[str] = None
    testimonial2_author: Optional[str] = None
    testimonial2_visible: Optional[int] = None
    latest_news_section_title: Optional[str] = None
    latest_news_section_visible: Optional[int] = None
    newsletter_section_title: Optional[str] = None
    newsletter_section_visible: Optional[int] = None
    # Gallery page specific
    gallery_filter_section_visible: Optional[int] = None
    # Contact page specific
    contact_info_section_visible: Optional[int] = None
    contact_form_section_visible: Optional[int] = None
    contact_partner_section_visible: Optional[int] = None
    contact_partner_title: Optional[str] = None
    contact_partner_content: Optional[str] = None
    contact_partner_button_text: Optional[str] = None
    contact_partner_button_url: Optional[str] = None
    # Blog page specific
    blog_header_visible: Optional[int] = None
    is_published: Optional[int] = None

class PageResponse(PageBase):
    id: int
    is_published: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "contributor"  # contributor, admin, super_admin
    is_active: int = 1

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

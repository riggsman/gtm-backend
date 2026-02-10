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
    category: Optional[str] = None
    author: Optional[str] = None

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

class TestimonialBase(BaseModel):
    title: str
    content: str
    author: str
    order: int = 0
    is_active: int = 1

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[int] = None

class TestimonialResponse(TestimonialBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    is_downloadable: int = 1
    is_viewable: int = 1
    prevent_screenshots: int = 0
    is_visible: int = 1
    order: int = 0

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_downloadable: Optional[int] = None
    is_viewable: Optional[int] = None
    prevent_screenshots: Optional[int] = None
    is_visible: Optional[int] = None
    order: Optional[int] = None

class DocumentResponse(DocumentBase):
    id: int
    file_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AboutBase(BaseModel):
    title: Optional[str] = "About"
    page_header_title: Optional[str] = "About Us"
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = 1
    history: Optional[str] = None
    history_visible: Optional[int] = 1
    mission: Optional[str] = None
    mission_visible: Optional[int] = 1
    vision: Optional[str] = None
    vision_visible: Optional[int] = 1
    values: Optional[str] = None  # JSON string or comma-separated
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
    is_published: Optional[int] = 0

class AboutCreate(AboutBase):
    pass

class AboutUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
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
    is_published: Optional[int] = None

class AboutResponse(AboutBase):
    id: int
    published_at: Optional[datetime] = None
    # created_at: str
    # updated_at: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
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
    hero_title: Optional[str] = "Welcome To\nThe Throne of God Ministry Intrnational"
    hero_subtitle: Optional[str] = "Grow your faith via our institutions and make a difference in knowing Jesus Christ"
    hero_button1_text: Optional[str] = "I give my ife to Christ"
    hero_button1_url: Optional[str] = ""
    hero_button1_visible: Optional[int] = 1
    hero_button2_text: Optional[str] = "Become a partner"
    hero_button2_url: Optional[str] = ""
    hero_button2_visible: Optional[int] = 1
    hero_image_url: Optional[str] = None
    hero_image_visible: Optional[int] = None
    hero_background_image_url: Optional[str] = None
    hero_background_image_visible: Optional[int] = None
    hero_layout_direction: Optional[str] = "left"  # "left" = text left/image right, "right" = image left/text right
    # Email notification settings
    admin_emails: Optional[str] = None
    # SMTP server configuration
    smtp_sender_email: Optional[str] = None
    smtp_sender_password: Optional[str] = None
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    # Admin panel settings
    admin_panel_title: Optional[str] = "Glorious Church"
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
    # Social media links
    social_facebook_url: Optional[str] = None
    social_twitter_url: Optional[str] = None
    social_instagram_url: Optional[str] = None
    social_youtube_url: Optional[str] = None
    social_linkedin_url: Optional[str] = None
    social_section_visible: Optional[int] = 0
    # Quick links
    quick_links_section_visible: Optional[int] = 0
    quick_links_pages: Optional[str] = None  # JSON array of page names
    # Contact information
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    contact_office_hours: Optional[str] = None
    contact_section_visible: Optional[int] = 0
    # Partner section (Become a Partner)
    partner_section_visible: Optional[int] = 1
    partner_section_title: Optional[str] = "Become a Partner"
    partner_section_content: Optional[str] = None
    partner_section_button_text: Optional[str] = "Partner With Us"
    partner_section_button_url: Optional[str] = "contact.html"
    # Statistics section (Our Numbers)
    statistics_section_visible: Optional[int] = 1
    statistics_section_title: Optional[str] = "OUR NUMBERS"

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
    hero_layout_direction: Optional[str] = None
    # Email notification settings
    admin_emails: Optional[str] = None
    # SMTP server configuration
    smtp_sender_email: Optional[str] = None
    smtp_sender_password: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    # Admin panel settings
    admin_panel_title: Optional[str] = "Glorious Church"
    # Social media links
    social_facebook_url: Optional[str] = None
    social_twitter_url: Optional[str] = None
    social_instagram_url: Optional[str] = None
    social_youtube_url: Optional[str] = None
    social_linkedin_url: Optional[str] = None
    social_section_visible: Optional[int] = None
    # Quick links
    quick_links_section_visible: Optional[int] = None
    quick_links_pages: Optional[str] = None
    # Contact information
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    contact_office_hours: Optional[str] = None
    contact_section_visible: Optional[int] = None
    # Partner section (Become a Partner)
    partner_section_visible: Optional[int] = None
    partner_section_title: Optional[str] = None
    partner_section_content: Optional[str] = None
    partner_section_button_text: Optional[str] = None
    partner_section_button_url: Optional[str] = None
    # Statistics section (Our Numbers)
    statistics_section_visible: Optional[int] = None
    statistics_section_title: Optional[str] = None

class SiteSettingsResponse(SiteSettingsBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Page schemas
# Home Page Schemas
class HomePageBase(BaseModel):
    title: Optional[str] = "Home"
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = 1
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
    is_published: Optional[int] = 0

class HomePageCreate(HomePageBase):
    pass

class HomePageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
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
    is_published: Optional[int] = None

class HomePageResponse(HomePageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Contact Page Schemas
class ContactPageBase(BaseModel):
    title: Optional[str] = "Contact"
    page_header_title: Optional[str] = "Contact Us"
    page_header_subtitle: Optional[str] = "Get in Touch"
    page_header_visible: Optional[int] = 1
    contact_info_section_visible: Optional[int] = 1
    contact_form_section_visible: Optional[int] = 1
    contact_partner_section_visible: Optional[int] = 1
    contact_partner_title: Optional[str] = None
    contact_partner_content: Optional[str] = None
    contact_partner_button_text: Optional[str] = None
    contact_partner_button_url: Optional[str] = None
    is_published: Optional[int] = 0

class ContactPageCreate(ContactPageBase):
    pass

class ContactPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    contact_info_section_visible: Optional[int] = None
    contact_form_section_visible: Optional[int] = None
    contact_partner_section_visible: Optional[int] = None
    contact_partner_title: Optional[str] = None
    contact_partner_content: Optional[str] = None
    contact_partner_button_text: Optional[str] = None
    contact_partner_button_url: Optional[str] = None
    is_published: Optional[int] = None

class ContactPageResponse(ContactPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Blog Page Schemas
class BlogPageBase(BaseModel):
    title: Optional[str] = "Blog"
    page_header_title: Optional[str] = "Blog"
    page_header_subtitle: Optional[str] = "Latest News & Updates"
    page_header_visible: Optional[int] = 1
    blog_content_section_visible: Optional[int] = 1
    blog_sidebar_section_visible: Optional[int] = 1
    blog_recent_posts_section_visible: Optional[int] = 1
    blog_categories_section_visible: Optional[int] = 1
    blog_newsletter_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class BlogPageCreate(BlogPageBase):
    pass

class BlogPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    blog_content_section_visible: Optional[int] = None
    blog_sidebar_section_visible: Optional[int] = None
    blog_recent_posts_section_visible: Optional[int] = None
    blog_categories_section_visible: Optional[int] = None
    blog_newsletter_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class BlogPageResponse(BlogPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Gallery Page Schemas
class GalleryPageBase(BaseModel):
    title: Optional[str] = "Gallery"
    page_header_title: Optional[str] = "Gallery"
    page_header_subtitle: Optional[str] = "Our Church in Pictures"
    page_header_visible: Optional[int] = 1
    gallery_filter_section_visible: Optional[int] = 1
    gallery_content_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class GalleryPageCreate(GalleryPageBase):
    pass

class GalleryPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    gallery_filter_section_visible: Optional[int] = None
    gallery_content_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class GalleryPageResponse(GalleryPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Branches Page Schemas
class BranchesPageBase(BaseModel):
    title: Optional[str] = "Branches"
    page_header_title: Optional[str] = "Branches"
    page_header_subtitle: Optional[str] = "Our Regional Offices"
    page_header_visible: Optional[int] = 1
    branches_content_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class BranchesPageCreate(BranchesPageBase):
    pass

class BranchesPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    branches_content_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class BranchesPageResponse(BranchesPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Departments Page Schemas
class DepartmentsPageBase(BaseModel):
    title: Optional[str] = "Departments"
    page_header_title: Optional[str] = "Departments"
    page_header_subtitle: Optional[str] = "Our Organizational Structure"
    page_header_visible: Optional[int] = 1
    departments_content_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class DepartmentsPageCreate(DepartmentsPageBase):
    pass

class DepartmentsPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    departments_content_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class DepartmentsPageResponse(DepartmentsPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Events Page Schemas
class EventsPageBase(BaseModel):
    title: Optional[str] = "Events"
    page_header_title: Optional[str] = "Our Events"
    page_header_subtitle: Optional[str] = "Stay updated with our upcoming events and activities"
    page_header_visible: Optional[int] = 1
    events_content_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class EventsPageCreate(EventsPageBase):
    pass

class EventsPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    events_content_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class EventsPageResponse(EventsPageBase):
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Documents Page Schemas
class DocumentsPageBase(BaseModel):
    title: Optional[str] = "Documents"
    page_header_title: Optional[str] = "Documents"
    page_header_subtitle: Optional[str] = "Browse and download our documents"
    page_header_visible: Optional[int] = 1
    documents_content_section_visible: Optional[int] = 1
    is_published: Optional[int] = 0

class DocumentsPageCreate(DocumentsPageBase):
    pass

class DocumentsPageUpdate(BaseModel):
    title: Optional[str] = None
    page_header_title: Optional[str] = None
    page_header_subtitle: Optional[str] = None
    page_header_visible: Optional[int] = None
    documents_content_section_visible: Optional[int] = None
    is_published: Optional[int] = None

class DocumentsPageResponse(DocumentsPageBase):
    id: int
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

# DEPRECATED: AboutContent Schemas - Use About schemas instead
# These schemas are kept for backward compatibility but should not be used in new code
# All new code should use AboutBase, AboutCreate, AboutUpdate, AboutResponse
# class AboutContentBase(BaseModel):
#     title: Optional[str] = "About Us"
#     content: Optional[str] = None
#     mission: Optional[str] = None
#     vision: Optional[str] = None
#     values: Optional[str] = None
#     history: Optional[str] = None
#     leadership: Optional[str] = None
#     is_published: Optional[int] = 1
#
# class AboutContentCreate(AboutContentBase):
#     pass
#
# class AboutContentUpdate(AboutContentBase):
#     pass
#
# class AboutContentResponse(AboutContentBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     updated_by: Optional[int] = None
#     
#     class Config:
#         from_attributes = True

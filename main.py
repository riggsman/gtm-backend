from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import asyncio

from database import SessionLocal, engine, Base
from models import Branch, Department, BlogPost, ContactMessage, Event, GalleryImage, About, NavigationItem, SiteSettings, Page, User
from schemas import (
    BranchCreate, BranchResponse,
    DepartmentCreate, DepartmentResponse,
    BlogPostCreate, BlogPostResponse,
    ContactMessageCreate, ContactMessageResponse,
    EventCreate, EventResponse,
    GalleryImageCreate, GalleryImageResponse,
    AboutCreate, AboutResponse,
    NavigationItemCreate, NavigationItemUpdate, NavigationItemResponse,
    SiteSettingsUpdate, SiteSettingsResponse,
    PageCreate, PageUpdate, PageResponse,
    UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
)
from auth import hash_password, verify_token, create_access_token, get_password_hash, verify_password, get_current_user
from config import settings
from email_service import send_email_notification

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Glorious Church CMS API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/gallery", exist_ok=True)
os.makedirs("uploads/blog", exist_ok=True)
os.makedirs("uploads/hero", exist_ok=True)
os.makedirs("uploads/departments", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SUPER_ADMIN_ROLE = ["super_admin"]
ADMINS_ROLES = ["admin", "super_admin"]
CONTRIBUTORS_ROLES = ["contributor", "admin", "super_admin"]

# ============ AUTH ENDPOINTS ============
@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """User login - supports both User model and legacy admin"""
    # Try User model first
    user = db.query(User).filter(User.username == login_data.username).first()
    if user and verify_password(login_data.password, user.password_hash):
        if user.is_active == 0:
            raise HTTPException(status_code=401, detail="User account is inactive")
        token = create_access_token({
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
    
    # Fallback to legacy admin (for backward compatibility)
    if login_data.username == settings.ADMIN_USERNAME and verify_password(login_data.password, settings.ADMIN_PASSWORD_HASH):
        # Create a temporary user response for legacy admin
        from schemas import UserResponse as LegacyUserResponse
        legacy_user = type('obj', (object,), {
            'id': 0,
            'username': settings.ADMIN_USERNAME,
            'email': '',
            'role': 'super_admin',
            'is_active': 1,
            'created_at': datetime.now(),
            'updated_at': None,
            'created_by': None
        })()
        token = create_access_token({
            "sub": settings.ADMIN_USERNAME,
            "user_id": 0,
            "role": "super_admin"
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": legacy_user
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============ BRANCHES ENDPOINTS ============
@app.get("/api/branches", response_model=List[BranchResponse])
def get_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all branches"""
    branches = db.query(Branch).offset(skip).limit(limit).all()
    return branches

@app.post("/api/branches", response_model=BranchResponse)
def create_branch(branch: BranchCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create a new branch (Admin only)"""
    db_branch = Branch(**branch.dict())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@app.put("/api/branches/{branch_id}", response_model=BranchResponse)
def update_branch(branch_id: int, branch: BranchCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update a branch (Admin only)"""
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, value in branch.dict().items():
        setattr(db_branch, key, value)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@app.delete("/api/branches/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a branch (Admin only)"""
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(db_branch)
    db.commit()
    return {"message": "Branch deleted successfully"}

# ============ DEPARTMENTS ENDPOINTS ============
@app.get("/api/departments", response_model=List[DepartmentResponse])
def get_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments

@app.get("/api/departments/{id}", response_model=DepartmentResponse)
def get_departments(id:int, db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).filter(Department.id == id).first()
    return departments

@app.post("/api/departments", response_model=DepartmentResponse)
def create_department(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    icon: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Create a new department (Admin only)"""
    image_url = None
    if image:
        filename = f"dept_{datetime.now().timestamp()}_{image.filename}"
        filepath = os.path.join("uploads/departments", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/uploads/departments/{filename}"
    
    db_department = Department(name=name, description=description, icon=icon, image_url=image_url)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@app.put("/api/departments/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    icon: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),  # For deletion (empty string)
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Update a department (Admin only)"""
    db_department = db.query(Department).filter(Department.id == dept_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Update basic fields
    db_department.name = name
    db_department.description = description
    db_department.icon = icon
    
    # Handle image upload
    if image:
        # Delete old image if exists
        if db_department.image_url:
            old_path = db_department.image_url.replace("/uploads/", "uploads/")
            if os.path.exists(old_path):
                os.remove(old_path)
        # Save new image
        filename = f"dept_{datetime.now().timestamp()}_{image.filename}"
        filepath = os.path.join("uploads/departments", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_department.image_url = f"/uploads/departments/{filename}"
    
    # Handle image deletion (empty string means delete)
    if image_url is not None and image_url == '':
        if db_department.image_url:
            old_path = db_department.image_url.replace("/uploads/", "uploads/")
            if os.path.exists(old_path):
                os.remove(old_path)
        db_department.image_url = None
    
    db.commit()
    db.refresh(db_department)
    return db_department

@app.delete("/api/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a department (Admin only)"""
    db_department = db.query(Department).filter(Department.id == dept_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Delete associated image file if exists
    if db_department.image_url:
        old_path = db_department.image_url.replace("/uploads/", "uploads/")
        if os.path.exists(old_path):
            os.remove(old_path)
    
    db.delete(db_department)
    db.commit()
    return {"message": "Department deleted successfully"}

# ============ BLOG ENDPOINTS ============
@app.get("/api/blog", response_model=List[BlogPostResponse])
def get_blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all blog posts"""
    posts = db.query(BlogPost).order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@app.get("/api/blog/{post_id}", response_model=BlogPostResponse)
def get_blog_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single blog post"""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post

@app.post("/api/blog", response_model=BlogPostResponse)
def create_blog_post(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Create a new blog post (Admin only)"""
    image_url = None
    if image:
        filename = f"blog_{datetime.now().timestamp()}_{image.filename}"
        filepath = os.path.join("uploads/blog", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/uploads/blog/{filename}"
    
    db_post = BlogPost(title=title, content=content, image_url=image_url)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.put("/api/blog/{post_id}", response_model=BlogPostResponse)
def update_blog_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Update a blog post (Admin only)"""
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    db_post.title = title
    db_post.content = content
    
    if image:
        if db_post.image_url:
            old_path = db_post.image_url.replace("/uploads/", "uploads/")
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = f"blog_{datetime.now().timestamp()}_{image.filename}"
        filepath = os.path.join("uploads/blog", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_post.image_url = f"/uploads/blog/{filename}"
    
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/api/blog/{post_id}")
def delete_blog_post(post_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a blog post (Admin only)"""
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if db_post.image_url:
        old_path = db_post.image_url.replace("/uploads/", "uploads/")
        if os.path.exists(old_path):
            os.remove(old_path)
    db.delete(db_post)
    db.commit()
    return {"message": "Blog post deleted successfully"}

# ============ CONTACT ENDPOINTS ============
@app.post("/api/contact", response_model=ContactMessageResponse)
async def create_contact_message(
    message: ContactMessageCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a contact message and send email notification to admins"""
    db_message = ContactMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send email notification in background
    background_tasks.add_task(send_notification_email, db_message, db)
    
    return db_message

def send_notification_email(message: ContactMessage, db: Session):
    """Background task to send email notification"""
    try:
        # Get admin emails from database
        settings = db.query(SiteSettings).first()
        if not settings or not settings.admin_emails:
            return
        
        # Send email notification (synchronous)
        # SMTP settings are read from environment variables
        send_email_notification(
            admin_emails=settings.admin_emails,
            sender_name=message.name,
            sender_email=message.email,
            subject=message.subject,
            message=message.message
        )
    except Exception as e:
        print(f"Error sending notification email: {e}")

@app.get("/api/contact", response_model=List[ContactMessageResponse])
def get_contact_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Get all contact messages (Admin only)"""
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).offset(skip).limit(limit).all()
    return messages


@app.delete("/api/contact/{message_id}")
def delete_contact_message(message_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a contact message (Admin only)"""
    db_message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    db.delete(db_message)
    db.commit()
    return {"message": "Contact message deleted successfully"}

# ============ EVENTS ENDPOINTS ============
@app.get("/api/events", response_model=List[EventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all events"""
    events = db.query(Event).order_by(Event.date.asc()).offset(skip).limit(limit).all()
    return events


@app.get("/api/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get an event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/api/events", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create a new event (Admin only)"""
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update an event (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete an event (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted successfully"}

# ============ GALLERY ENDPOINTS ============
@app.get("/api/gallery", response_model=List[GalleryImageResponse])
def get_gallery_images(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all gallery images"""
    query = db.query(GalleryImage)
    if category:
        query = query.filter(GalleryImage.category == category)
    images = query.order_by(GalleryImage.created_at.desc()).all()
    return images

@app.post("/api/gallery", response_model=GalleryImageResponse)
def create_gallery_image(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Upload a gallery image (Admin only)"""
    filename = f"gallery_{datetime.now().timestamp()}_{image.filename}"
    filepath = os.path.join("uploads/gallery", filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    image_url = f"/uploads/gallery/{filename}"
    
    db_image = GalleryImage(title=title, description=description, category=category, image_url=image_url)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@app.delete("/api/gallery/{image_id}")
def delete_gallery_image(image_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a gallery image (Admin only)"""
    db_image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    if db_image.image_url:
        old_path = db_image.image_url.replace("/uploads/", "uploads/")
        if os.path.exists(old_path):
            os.remove(old_path)
    db.delete(db_image)
    db.commit()
    return {"message": "Gallery image deleted successfully"}

# ============ ABOUT ENDPOINTS ============
@app.get("/api/about", response_model=AboutResponse)
def get_about(db: Session = Depends(get_db)):
    """Get about page content"""
    about = db.query(About).first()
    if not about:
        # Return default/empty about if none exists
        return AboutResponse(
            id=0,
            history=None,
            mission=None,
            vision=None,
            values=None,
            institutions=None,
            updated_at=datetime.now()
        )
    return about

@app.post("/api/about", response_model=AboutResponse)
def create_about(about: AboutCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create about page content (Admin only)"""
    # Check if about already exists
    existing = db.query(About).first()
    if existing:
        raise HTTPException(status_code=400, detail="About content already exists. Use PUT to update.")
    
    db_about = About(**about.dict())
    db.add(db_about)
    db.commit()
    db.refresh(db_about)
    return db_about

@app.put("/api/about", response_model=AboutResponse)
def update_about(about: AboutCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update about page content (Admin only)"""
    db_about = db.query(About).first()
    if not db_about:
        # Create if doesn't exist
        db_about = About(**about.dict())
        db.add(db_about)
    else:
        # Update existing
        for key, value in about.dict().items():
            setattr(db_about, key, value)
    
    db.commit()
    db.refresh(db_about)
    return db_about

# ============ NAVIGATION ENDPOINTS ============
@app.get("/api/navigation", response_model=List[NavigationItemResponse])
def get_navigation(db: Session = Depends(get_db)):
    """Get all active navigation items ordered by order"""
    items = db.query(NavigationItem).filter(NavigationItem.is_active == 1).order_by(NavigationItem.order.asc()).all()
    return items

@app.get("/api/navigation/all", response_model=List[NavigationItemResponse])
def get_all_navigation(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Get all navigation items including inactive (Admin only)"""
    items = db.query(NavigationItem).order_by(NavigationItem.order.asc()).all()
    return items

@app.post("/api/navigation", response_model=NavigationItemResponse)
def create_navigation_item(item: NavigationItemCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create a navigation item (Admin only)"""
    db_item = NavigationItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/api/navigation/{item_id}", response_model=NavigationItemResponse)
def update_navigation_item(item_id: int, item: NavigationItemUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update a navigation item (Admin only)"""
    db_item = db.query(NavigationItem).filter(NavigationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/navigation/{item_id}")
def delete_navigation_item(item_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a navigation item (Admin only)"""
    db_item = db.query(NavigationItem).filter(NavigationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Navigation item deleted successfully"}

# ============ SITE SETTINGS ENDPOINTS ============
@app.get("/api/settings", response_model=SiteSettingsResponse)
def get_site_settings(db: Session = Depends(get_db)):
    """Get site settings"""
    settings = db.query(SiteSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = SiteSettings(
            site_name="Glorious Church",
            tagline=None,
            hero_title="Welcome To\nThe Presbyterian Church In Cameroon",
            hero_subtitle="Grow your faith via our institutions and make a difference in knowing Jesus Christ",
            hero_button1_text="Live stream CBS Bamenda",
            hero_button1_url="#",
            hero_button2_text="Live Stream CBS Buea",
            hero_button2_url="#"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.put("/api/settings", response_model=SiteSettingsResponse)
def update_site_settings(
    hero_title: Optional[str] = Form(None),
    hero_subtitle: Optional[str] = Form(None),
    hero_button1_text: Optional[str] = Form(None),
    hero_button1_url: Optional[str] = Form(None),
    hero_button1_visible: Optional[str] = Form(None),
    hero_button2_text: Optional[str] = Form(None),
    hero_button2_url: Optional[str] = Form(None),
    hero_button2_visible: Optional[str] = Form(None),
    hero_image: Optional[UploadFile] = File(None),
    hero_background_image: Optional[UploadFile] = File(None),
    hero_image_url: Optional[str] = Form(None),  # For deletion (empty string)
    hero_image_visible: Optional[str] = Form(None),
    hero_background_image_url: Optional[str] = Form(None),  # For deletion (empty string)
    hero_background_image_visible: Optional[str] = Form(None),
    site_name: Optional[str] = Form(None),
    tagline: Optional[str] = Form(None),
    site_name_font_family: Optional[str] = Form(None),
    site_name_font_size: Optional[str] = Form(None),
    site_name_font_weight: Optional[str] = Form(None),
    site_name_color: Optional[str] = Form(None),
    tagline_font_family: Optional[str] = Form(None),
    tagline_font_size: Optional[str] = Form(None),
    tagline_font_weight: Optional[str] = Form(None),
    tagline_color: Optional[str] = Form(None),
    theme_primary: Optional[str] = Form(None),
    theme_secondary: Optional[str] = Form(None),
    theme_success: Optional[str] = Form(None),
    theme_danger: Optional[str] = Form(None),
    theme_warning: Optional[str] = Form(None),
    theme_info: Optional[str] = Form(None),
    theme_light: Optional[str] = Form(None),
    theme_dark: Optional[str] = Form(None),
    admin_emails: Optional[str] = Form(None),
    # Admin panel settings
    admin_panel_title: Optional[str] = Form(None),
    # Feature flags
    feature_dashboard: Optional[str] = Form(None),
    feature_blog: Optional[str] = Form(None),
    feature_branches: Optional[str] = Form(None),
    feature_departments: Optional[str] = Form(None),
    feature_events: Optional[str] = Form(None),
    feature_gallery: Optional[str] = Form(None),
    feature_contact: Optional[str] = Form(None),
    feature_pages: Optional[str] = Form(None),
    feature_about: Optional[str] = Form(None),
    feature_navigation: Optional[str] = Form(None),
    feature_users: Optional[str] = Form(None),
    feature_settings: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Update site settings (Admin only)"""
    settings = db.query(SiteSettings).first()
    if not settings:
        settings = SiteSettings()
        db.add(settings)
    
    # Handle hero image upload
    if hero_image:
        if settings.hero_image_url:
            old_path = settings.hero_image_url.replace("/uploads/", "uploads/")
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = f"hero_{datetime.now().timestamp()}_{hero_image.filename}"
        filepath = os.path.join("uploads/hero", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(hero_image.file, buffer)
        settings.hero_image_url = f"/uploads/hero/{filename}"
    
    # Handle hero background image upload
    if hero_background_image:
        if settings.hero_background_image_url:
            old_path = settings.hero_background_image_url.replace("/uploads/", "uploads/")
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = f"hero_bg_{datetime.now().timestamp()}_{hero_background_image.filename}"
        filepath = os.path.join("uploads/hero", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(hero_background_image.file, buffer)
        settings.hero_background_image_url = f"/uploads/hero/{filename}"
    
    # Handle image deletion (empty string means delete)
    # Check if hero_image_url is explicitly set to empty string (deletion request)
    if hero_image_url is not None:
        if hero_image_url == '':
            # Delete the image file
            if settings.hero_image_url:
                old_path = settings.hero_image_url.replace("/uploads/", "uploads/")
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting hero image: {e}")
            settings.hero_image_url = None
            settings.hero_image_visible = 0  # Hide when deleted
    
    if hero_background_image_url is not None:
        if hero_background_image_url == '':
            # Delete the image file
            if settings.hero_background_image_url:
                old_path = settings.hero_background_image_url.replace("/uploads/", "uploads/")
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting background image: {e}")
            settings.hero_background_image_url = None
            settings.hero_background_image_visible = 0  # Hide when deleted
    
    # Update all other fields
    update_fields = {
        'hero_title': hero_title,
        'hero_subtitle': hero_subtitle,
        'hero_button1_text': hero_button1_text,
        'hero_button1_url': hero_button1_url,
        'hero_button1_visible': int(hero_button1_visible) if hero_button1_visible else None,
        'hero_button2_text': hero_button2_text,
        'hero_button2_url': hero_button2_url,
        'hero_button2_visible': int(hero_button2_visible) if hero_button2_visible else None,
        'hero_image_visible': int(hero_image_visible) if hero_image_visible else None,
        'hero_background_image_visible': int(hero_background_image_visible) if hero_background_image_visible else None,
        'site_name': site_name,
        'tagline': tagline,
        'site_name_font_family': site_name_font_family,
        'site_name_font_size': site_name_font_size,
        'site_name_font_weight': site_name_font_weight,
        'site_name_color': site_name_color,
        'tagline_font_family': tagline_font_family,
        'tagline_font_size': tagline_font_size,
        'tagline_font_weight': tagline_font_weight,
        'tagline_color': tagline_color,
        'theme_primary': theme_primary,
        'theme_secondary': theme_secondary,
        'theme_success': theme_success,
        'theme_danger': theme_danger,
        'theme_warning': theme_warning,
        'theme_info': theme_info,
        'theme_light': theme_light,
        'theme_dark': theme_dark,
        'admin_emails': admin_emails,
        'admin_panel_title': admin_panel_title
    }
    
    # Update feature flags
    feature_flags = {
        'feature_dashboard': feature_dashboard,
        'feature_blog': feature_blog,
        'feature_branches': feature_branches,
        'feature_departments': feature_departments,
        'feature_events': feature_events,
        'feature_gallery': feature_gallery,
        'feature_contact': feature_contact,
        'feature_pages': feature_pages,
        'feature_about': feature_about,
        'feature_navigation': feature_navigation,
        'feature_users': feature_users,
        'feature_settings': feature_settings,
    }
    
    for flag_name, flag_value in feature_flags.items():
        if flag_value is not None:
            # Convert string "1" or "0" to int
            setattr(settings, flag_name, 1 if flag_value == '1' or flag_value == 'true' else 0)
    
    for key, value in update_fields.items():
        if value is not None:
            setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    return settings

# ============ PERMISSION HELPERS ============
def check_permission(user: dict, required_permission: str):
    """Check if user has required permission"""
    role = user.get("role", "contributor")
    
    # Permission mapping
    permissions = {
        "contributor": ["write", "update"],
        "admin": ["write", "update", "read", "delete"],
        "super_admin": ["write", "update", "read", "delete", "create_user", "manage_users"]
    }
    
    user_perms = permissions.get(role, [])
    if required_permission not in user_perms:
        raise HTTPException(status_code=403, detail=f"Insufficient permissions. Required: {required_permission}")

def require_role(user: dict, allowed_roles: list):
    """Check if user has one of the allowed roles"""
    role = user.get("role", "contributor")
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"Access denied. Required roles: {', '.join(allowed_roles)}")

# ============ UPDATED AUTH ENDPOINTS ============
# Keep old login for backward compatibility, but also support new user system
@app.post("/api/auth/login")
def login(username: str = Form(None), password: str = Form(None), login_data: UserLogin = None, db: Session = Depends(get_db)):
    """User login - supports both Form (legacy) and JSON (new)"""
    # Handle form data (legacy)
    if username and password:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            if user.is_active == 0:
                raise HTTPException(status_code=401, detail="User account is inactive")
            token = create_access_token({
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            })
            return {"access_token": token, "token_type": "bearer", "user": user}
        
        # Fallback to legacy admin
        if username == settings.ADMIN_USERNAME and verify_password(password, settings.ADMIN_PASSWORD_HASH):
            token = create_access_token({
                "sub": settings.ADMIN_USERNAME,
                "user_id": 0,
                "role": "super_admin"
            })
            return {"access_token": token, "token_type": "bearer"}
    
    # Handle JSON data (new)
    if login_data:
        user = db.query(User).filter(User.username == login_data.username).first()
        if user and verify_password(login_data.password, user.password_hash):
            if user.is_active == 0:
                raise HTTPException(status_code=401, detail="User account is inactive")
            token = create_access_token({
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            })
            return {"access_token": token, "token_type": "bearer", "user": user}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============ PAGES ENDPOINTS ============
@app.get("/api/pages", response_model=List[PageResponse])
def get_pages(include_drafts: bool = False, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get all pages (Admin only, includes drafts if include_drafts=True)"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    if include_drafts:
        pages = db.query(Page).all()
    else:
        pages = db.query(Page).filter(Page.is_published == 1).all()
    return pages

@app.get("/api/pages/{page_name}", response_model=PageResponse)
def get_page(page_name: str, include_draft: bool = False, db: Session = Depends(get_db)):
    """Get a page by name (public endpoint, only returns published unless include_draft=True and user is admin)"""
    page = db.query(Page).filter(Page.page_name == page_name).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Only return published pages to public, unless explicitly requesting draft
    if not include_draft and page.is_published == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return page

@app.get("/api/pages/drafts/count")
def get_drafts_count(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get count of unpublished pages (Admin only)"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    count = db.query(Page).filter(Page.is_published == 0).count()
    return {"count": count}

@app.post("/api/pages", response_model=PageResponse)
def create_page(page: PageCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create a new page (Admin only)"""
    check_permission(current_user, "write")
    
    # Check if page already exists
    existing = db.query(Page).filter(Page.page_name == page.page_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Page with this name already exists")
    
    # Ensure is_published is set (default to 0 if not specified)
    page_dict = page.dict()
    if "is_published" not in page_dict or page_dict["is_published"] is None:
        page_dict["is_published"] = 0
    
    db_page = Page(**page_dict, created_by=current_user["user_id"], updated_by=current_user["user_id"])
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

@app.put("/api/pages/{page_id}", response_model=PageResponse)
def update_page(page_id: int, page: PageUpdate, publish: bool = False, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Update a page (Admin only). Use publish=True to publish, False to save as draft"""
    check_permission(current_user, "write")
    
    db_page = db.query(Page).filter(Page.id == page_id).first()
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Update fields
    # Use exclude_none=False to ensure 0 values are included
    update_data = page.dict(exclude_unset=True, exclude_none=False)
    
    # First, explicitly handle visibility fields - they should always be updated
    # Get all visibility fields that might be updated
    visibility_fields = ['page_header_visible', 'history_visible', 'mission_visible', 'vision_visible', 
                        'values_visible', 'institutions_visible', 
                        'content1_visible', 'content2_visible', 'content3_visible',
                        'news_section_visible', 'partner_section_visible', 'events_section_visible',
                        'statistics_section_visible', 'partners_faith_section_visible',
                        'testimonials_section_visible', 'testimonial1_visible', 'testimonial2_visible',
                        'latest_news_section_visible', 'newsletter_section_visible',
                        'gallery_filter_section_visible', 'gallery_content_section_visible',
                        'contact_info_section_visible', 'contact_form_section_visible', 
                        'contact_partner_section_visible',
                        'blog_content_section_visible', 'blog_sidebar_section_visible',
                        'blog_recent_posts_section_visible', 'blog_categories_section_visible',
                        'blog_newsletter_section_visible',
                        'branches_content_section_visible', 'departments_content_section_visible',
                        'events_content_section_visible']
    
    # Always update visibility fields if they're in update_data
    # This ensures that toggles work correctly (0 or 1)
    for field in visibility_fields:
        if field in update_data:
            value = update_data[field]
            # Convert to int and ensure it's 0 or 1 (explicitly handle 0 as a valid value)
            if value is not None:
                int_value = int(value)
                setattr(db_page, field, 1 if int_value == 1 else 0)
            # If value is None, don't update (keep existing value)
    
    # Then update other fields (excluding visibility fields and is_published)
    for key, value in update_data.items():
        if not key.endswith('_visible') and key != 'is_published' and value is not None:
            setattr(db_page, key, value)
    
    # Handle publish status
    if publish:
        db_page.is_published = 1
        db_page.published_at = datetime.now()
    else:
        # Save as draft - explicitly set to draft if not publishing
        if "is_published" in update_data:
            # If explicitly set in update_data, use that value
            if update_data["is_published"] == 1:
                db_page.published_at = datetime.now()
            else:
                db_page.is_published = 0
        else:
            # If not explicitly set and not publishing, keep as draft
            db_page.is_published = 0
    
    db_page.updated_by = current_user["user_id"]
    db.commit()
    db.refresh(db_page)
    return db_page

@app.delete("/api/pages/{page_id}")
def delete_page(page_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Delete a page (Admin only)"""
    check_permission(current_user, "delete")
    
    db_page = db.query(Page).filter(Page.id == page_id).first()
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    db.delete(db_page)
    db.commit()
    return {"message": "Page deleted successfully"}

# ============ USERS ENDPOINTS ============
@app.get("/api/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get all users (Super Admin only)"""
    require_role(current_user, SUPER_ADMIN_ROLE)
    users = db.query(User).all()
    return users

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create a new user (Super Admin only)"""
    require_role(current_user, SUPER_ADMIN_ROLE)
    
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role,
        is_active=user.is_active,
        created_by=current_user["user_id"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Update a user (Super Admin only)"""
    require_role(current_user, SUPER_ADMIN_ROLE)
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password" and value:
            setattr(db_user, "password_hash", get_password_hash(value))
        elif key != "password":
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Delete a user (Super Admin only)"""
    require_role(current_user, SUPER_ADMIN_ROLE)
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting yourself
    if db_user.id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

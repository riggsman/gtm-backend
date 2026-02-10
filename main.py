from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import os
import shutil
from datetime import datetime
import asyncio
import re

from database import SessionLocal, engine, Base
from models import (
    Branch, Department, BlogPost, ContactMessage, Event, GalleryImage, About, 
    NavigationItem, SiteSettings, User, Testimonial, Document,
    HomePage, ContactPage, BlogPage, GalleryPage, BranchesPage, DepartmentsPage, EventsPage, DocumentsPage
)
from sqlalchemy import text, inspect
from schemas import (
    BranchCreate, BranchResponse,
    DepartmentCreate, DepartmentResponse,
    BlogPostCreate, BlogPostResponse,
    ContactMessageCreate, ContactMessageResponse,
    EventCreate, EventResponse,
    GalleryImageCreate, GalleryImageResponse,
    AboutCreate, AboutUpdate, AboutResponse,
    NavigationItemCreate, NavigationItemUpdate, NavigationItemResponse,
    SiteSettingsUpdate, SiteSettingsResponse,
    UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse,
    TestimonialCreate, TestimonialUpdate, TestimonialResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
    HomePageCreate, HomePageUpdate, HomePageResponse,
    ContactPageCreate, ContactPageUpdate, ContactPageResponse,
    BlogPageCreate, BlogPageUpdate, BlogPageResponse,
    GalleryPageCreate, GalleryPageUpdate, GalleryPageResponse,
    BranchesPageCreate, BranchesPageUpdate, BranchesPageResponse,
    DepartmentsPageCreate, DepartmentsPageUpdate, DepartmentsPageResponse,
    EventsPageCreate, EventsPageUpdate, EventsPageResponse,
    DocumentsPageCreate, DocumentsPageUpdate, DocumentsPageResponse
)
from auth import hash_password, verify_token, create_access_token, get_password_hash, verify_password, get_current_user
from config import settings
from email_service import send_email_notification

# Database tables are created via Alembic migrations
# Run: alembic upgrade head

app = FastAPI(title="Glorious Church CMS API")

@app.on_event("startup")
async def startup_event():
    pass

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
os.makedirs("uploads/documents", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to update .env file with SMTP settings
def update_env_file(smtp_sender_email: Optional[str] = None, 
                    smtp_sender_password: Optional[str] = None,
                    smtp_host: Optional[str] = None,
                    smtp_port: Optional[int] = None):
    """
    Update the .env file with SMTP configuration settings.
    Creates the file if it doesn't exist, or updates existing values.
    """
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), 'env.example')
    
    # Read existing .env file if it exists, otherwise read from env.example
    env_content = ""
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    elif os.path.exists(env_example_path):
        with open(env_example_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Update SMTP settings
    updates = {}
    if smtp_sender_email is not None:
        updates['SMTP_USERNAME'] = smtp_sender_email
    if smtp_sender_password is not None:
        updates['SMTP_PASSWORD'] = smtp_sender_password
    if smtp_host is not None:
        updates['SMTP_SERVER'] = smtp_host
    if smtp_port is not None:
        updates['SMTP_PORT'] = str(smtp_port)
    
    # Update or add each setting
    for key, value in updates.items():
        # Pattern to match the key (with or without value)
        pattern = rf'^{re.escape(key)}=.*$'
        replacement = f'{key}={value}'
        
        if re.search(pattern, env_content, re.MULTILINE):
            # Update existing line
            env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
        else:
            # Add new line (find Email Settings section or add at end)
            email_section_pattern = r'(# Email Settings.*?)(?=\n#|\Z)'
            email_match = re.search(email_section_pattern, env_content, re.DOTALL)
            
            if email_match:
                # Add after the email section comment
                email_section = email_match.group(1)
                if key not in email_section:
                    env_content = env_content.replace(
                        email_match.group(0),
                        email_match.group(0) + f'\n{key}={value}'
                    )
            else:
                # Add at the end of file
                if env_content and not env_content.endswith('\n'):
                    env_content += '\n'
                env_content += f'\n# Email Settings (SMTP)\n{key}={value}'
    
    # Write updated content back to .env file
    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.write(env_content)


SUPER_ADMIN_ROLE = ["super_admin"]
ADMINS_ROLES = ["admin", "super_admin"]
CONTRIBUTORS_ROLES = ["contributor", "admin", "super_admin"]

# ============ HEALTH CHECK ============
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Glorious Church CMS API"}

# ============ AUTH ENDPOINTS ============
@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """User login - supports both User model and legacy admin"""
    # Try User model first
    user = db.query(User).filter(User.username == login_data.username).first()
    if user:
        if verify_password(login_data.password, user.password_hash):
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
    if login_data.username == settings.ADMIN_USERNAME: 
        if verify_password(login_data.password, settings.ADMIN_PASSWORD_HASH):
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
    category: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
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
    
    db_post = BlogPost(title=title, content=content, image_url=image_url, category=category, author=author)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.put("/api/blog/{post_id}", response_model=BlogPostResponse)
def update_blog_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    category: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
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
    if category is not None:
        db_post.category = category
    if author is not None:
        db_post.author = author
    
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
        # SMTP settings are read from database (SiteSettings) or fallback to environment variables
        send_email_notification(
            admin_emails=settings.admin_emails,
            sender_name=message.name,
            sender_email=message.email,
            subject=message.subject,
            message=message.message,
            smtp_sender_email=settings.smtp_sender_email,
            smtp_sender_password=settings.smtp_sender_password,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port
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

# ============ TESTIMONIALS ENDPOINTS ============
@app.get("/api/testimonials", response_model=List[TestimonialResponse])
def get_testimonials(db: Session = Depends(get_db)):
    """Get all active testimonials ordered by order field"""
    testimonials = db.query(Testimonial).filter(Testimonial.is_active == 1).order_by(Testimonial.order.asc()).all()
    return testimonials

@app.get("/api/testimonials/all", response_model=List[TestimonialResponse])
def get_all_testimonials(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Get all testimonials including inactive (Admin only)"""
    testimonials = db.query(Testimonial).order_by(Testimonial.order.asc(), Testimonial.created_at.desc()).all()
    return testimonials

@app.get("/api/testimonials/{testimonial_id}", response_model=TestimonialResponse)
def get_testimonial(testimonial_id: int, db: Session = Depends(get_db)):
    """Get a single testimonial by ID"""
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return testimonial

@app.post("/api/testimonials", response_model=TestimonialResponse)
def create_testimonial(testimonial: TestimonialCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create a new testimonial (Admin only)"""
    db_testimonial = Testimonial(**testimonial.dict())
    db.add(db_testimonial)
    db.commit()
    db.refresh(db_testimonial)
    return db_testimonial

@app.put("/api/testimonials/{testimonial_id}", response_model=TestimonialResponse)
def update_testimonial(testimonial_id: int, testimonial: TestimonialUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update a testimonial (Admin only)"""
    db_testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not db_testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    for key, value in testimonial.dict(exclude_unset=True).items():
        setattr(db_testimonial, key, value)
    
    db.commit()
    db.refresh(db_testimonial)
    return db_testimonial

@app.delete("/api/testimonials/{testimonial_id}")
def delete_testimonial(testimonial_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a testimonial (Admin only)"""
    db_testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not db_testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    db.delete(db_testimonial)
    db.commit()
    return {"message": "Testimonial deleted successfully"}

# ============ DOCUMENTS ENDPOINTS ============
@app.get("/api/documents", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """Get all visible documents"""
    documents = db.query(Document).filter(Document.is_visible == 1).order_by(Document.order.asc(), Document.created_at.desc()).all()
    return documents

@app.get("/api/documents/all", response_model=List[DocumentResponse])
def get_all_documents(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Get all documents including hidden (Admin only)"""
    documents = db.query(Document).order_by(Document.order.asc(), Document.created_at.desc()).all()
    return documents

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a single document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.is_visible != 1:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/api/documents/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download a document file (Public endpoint - no auth required)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.is_visible != 1:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.is_downloadable != 1:
        raise HTTPException(status_code=403, detail="Document is not downloadable")
    
    file_path = document.file_url.replace("/uploads/", "uploads/")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Get the original filename with extension
    original_filename = os.path.basename(document.file_url)
    # If document has a title, use it with the original extension
    if document.title and document.file_type:
        # Clean the title for filename (remove invalid characters)
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', document.title)
        filename = f"{safe_title}.{document.file_type}"
    else:
        filename = original_filename
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream',
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.post("/api/documents", response_model=DocumentResponse)
def create_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_downloadable: int = Form(1),
    is_viewable: int = Form(1),
    prevent_screenshots: int = Form(0),
    is_visible: int = Form(1),
    order: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Upload a new document (Admin only)"""
    # Get file extension
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
    file_size = 0
    
    # Save file
    filename = f"doc_{datetime.now().timestamp()}_{file.filename}"
    filepath = os.path.join("uploads/documents", filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        file_size = os.path.getsize(filepath)
    
    file_url = f"/uploads/documents/{filename}"
    
    db_document = Document(
        title=title,
        file_url=file_url,
        file_type=file_extension,
        file_size=file_size,
        description=description,
        is_downloadable=is_downloadable,
        is_viewable=is_viewable,
        prevent_screenshots=prevent_screenshots,
        is_visible=is_visible,
        order=order
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.put("/api/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_downloadable: Optional[int] = Form(None),
    is_viewable: Optional[int] = Form(None),
    prevent_screenshots: Optional[int] = Form(None),
    is_visible: Optional[int] = Form(None),
    order: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Update a document (Admin only)"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if title is not None:
        db_document.title = title
    if description is not None:
        db_document.description = description
    if is_downloadable is not None:
        db_document.is_downloadable = is_downloadable
    if is_viewable is not None:
        db_document.is_viewable = is_viewable
    if prevent_screenshots is not None:
        db_document.prevent_screenshots = prevent_screenshots
    if is_visible is not None:
        db_document.is_visible = is_visible
    if order is not None:
        db_document.order = order
    
    db.commit()
    db.refresh(db_document)
    return db_document

@app.delete("/api/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete a document (Admin only)"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if db_document.file_url:
        file_path = db_document.file_url.replace("/uploads/", "uploads/")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.delete(db_document)
    db.commit()
    return {"message": "Document deleted successfully"}

# ============ ABOUT ENDPOINTS ============
@app.get("/api/about", response_model=AboutResponse)
def get_about(db: Session = Depends(get_db)):
    """Get about page content (public endpoint - only returns published content)"""
    about = db.query(About).first()
    if not about:
        # Return default if none exists
        return AboutResponse(
            id=0,
            title="About Us",
            page_header_title="About Us",
            page_header_subtitle=None,
            page_header_visible=1,
            history=None,
            history_visible=1,
            mission=None,
            mission_visible=1,
            vision=None,
            vision_visible=1,
            values=None,
            values_visible=1,
            institutions=None,
            institutions_visible=1,
            content1=None,
            content1_visible=1,
            content1_label="Content 1",
            content2=None,
            content2_visible=1,
            content2_label="Content 2",
            content3=None,
            content3_visible=1,
            content3_label="Content 3",
            is_published=1,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    # Only return if published (for public access)
    if about.is_published != 1:
        # Return default if not published
        return AboutResponse(
            id=0,
            title="About Us",
            page_header_title="About Us",
            page_header_subtitle=None,
            page_header_visible=1,
            history=None,
            history_visible=1,
            mission=None,
            mission_visible=1,
            vision=None,
            vision_visible=1,
            values=None,
            values_visible=1,
            institutions=None,
            institutions_visible=1,
            content1=None,
            content1_visible=1,
            content1_label="Content 1",
            content2=None,
            content2_visible=1,
            content2_label="Content 2",
            content3=None,
            content3_visible=1,
            content3_label="Content 3",
            is_published=1,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return about

@app.post("/api/about", response_model=AboutResponse)
def create_about(
    about: AboutCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create about page content (Admin only) - uses About model"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    
    # Check if about already exists
    existing = db.query(About).first()
    if existing:
        raise HTTPException(status_code=400, detail="About content already exists. Use PUT to update.")
    
    create_data = about.dict(exclude_unset=True)
    create_data['created_by'] = current_user["user_id"]
    create_data['updated_by'] = current_user["user_id"]
    
    db_about = About(**create_data)
    db.add(db_about)
    db.commit()
    db.refresh(db_about)
    return db_about

@app.put("/api/about", response_model=AboutResponse)
def update_about(
    about: AboutUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update about page content (Admin only) - uses About model"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    
    db_about = db.query(About).first()
    if not db_about:
        # Create if doesn't exist
        create_data = about.dict(exclude_unset=True)
        create_data['created_by'] = current_user["user_id"]
        create_data['updated_by'] = current_user["user_id"]
        if 'title' not in create_data or not create_data['title']:
            create_data['title'] = "About Us"
        db_about = About(**create_data)
        db.add(db_about)
    else:
        # Update existing
        update_data = about.dict(exclude_unset=True)
        update_data['updated_by'] = current_user["user_id"]
        for key, value in update_data.items():
            if hasattr(db_about, key):
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

@app.get("/api/files/html")
def get_html_files():
    """Scan and return all HTML files in the root directory (excluding admin folder) - Public endpoint"""
    html_files = []
    # Get the project root directory (parent of backend directory)
    current_file = os.path.abspath(__file__)  # backend/main.py
    backend_dir = os.path.dirname(current_file)  # backend/
    root_dir = os.path.dirname(backend_dir)  # project root
    
    try:
        # List all files in root directory
        for filename in os.listdir(root_dir):
            if filename.endswith('.html') and not filename.startswith('admin'):
                file_path = os.path.join(root_dir, filename)
                if os.path.isfile(file_path):
                    # Extract page name from filename (remove .html)
                    page_name = filename.replace('.html', '')
                    # Create a readable label (capitalize and replace hyphens)
                    label = page_name.replace('-', ' ').replace('_', ' ').title()
                    # Special handling for common pages
                    label_map = {
                        'index': 'Home',
                        'blog-detail': 'Blog Detail',
                    }
                    label = label_map.get(page_name, label)
                    
                    html_files.append({
                        "filename": filename,
                        "url": filename,
                        "label": label,
                        "page_name": page_name
                    })
        
        # Sort by filename
        html_files.sort(key=lambda x: x['filename'])
    except Exception as e:
        print(f"Error scanning HTML files: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"Found {len(html_files)} HTML files in {root_dir}")  # Debug log
    return html_files

@app.get("/api/files/html/{page_name}")
def get_html_file_content(page_name: str, db: Session = Depends(get_db)):
    """Get the content of a specific HTML file, with database content if available"""
    try:
        # First, check if there's a database entry for this page
        page = None
        try:
            config = get_page_config(page_name)
            model = config['model']
            page = db.query(model).first()
        except HTTPException:
            pass
        
        # If page exists in database and has HTML content, use it
        # Note: html_content field was removed, so we'll just read from file
        if page and hasattr(page, 'html_content') and page.html_content:
            return {
                "filename": f"{page_name}.html",
                "page_name": page_name,
                "content": page.html_content,
                "has_database_entry": True,
                "is_published": page.is_published if hasattr(page, 'is_published') else None
            }
        
        # Otherwise, load from file system
        # Get the project root directory
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file)
        root_dir = os.path.dirname(backend_dir)
        
        # Construct file path
        filename = f"{page_name}.html"
        file_path = os.path.join(root_dir, filename)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "filename": filename,
            "page_name": page_name,
            "content": content,
            "has_database_entry": page is not None,
            "is_published": page.is_published if page and hasattr(page, 'is_published') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.put("/api/files/html/{page_name}")
def update_html_file_content(page_name: str, file_data: dict, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Update the content of a specific HTML file (Admin only). Also saves to database if page exists."""
    try:
        # Get content from request
        content = file_data.get('content', '')
        if content is None:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Check if there's a database entry for this page
        page = None
        try:
            config = get_page_config(page_name)
            model = config['model']
            page = db.query(model).first()
        except HTTPException:
            pass
        
        # If page exists in database, save HTML content there
        # Note: html_content field was removed, so we'll just save to file
        if page and hasattr(page, 'html_content'):
            page.html_content = content
            db.commit()
            db.refresh(page)
            print(f"Page {page_name} HTML content saved to database")
        
        # Also save to file system
        # Get the project root directory
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file)
        root_dir = os.path.dirname(backend_dir)
        
        # Construct file path
        filename = f"{page_name}.html"
        file_path = os.path.join(root_dir, filename)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # Create backup before writing
        backup_path = file_path + '.backup'
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
        
        # Write file content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"File {filename} updated successfully")
        return {
            "message": "File updated successfully",
            "filename": filename,
            "page_name": page_name,
            "saved_to_database": page is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

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
    
    # Ensure visibility flags are integers (not None) for frontend
    if settings.quick_links_section_visible is None:
        settings.quick_links_section_visible = 0
    if settings.contact_section_visible is None:
        settings.contact_section_visible = 0
    if settings.social_section_visible is None:
        settings.social_section_visible = 0
    
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
    hero_layout_direction: Optional[str] = Form(None),  # "left" or "right"
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
    # Social media links
    social_facebook_url: Optional[str] = Form(None),
    social_twitter_url: Optional[str] = Form(None),
    social_instagram_url: Optional[str] = Form(None),
    social_youtube_url: Optional[str] = Form(None),
    social_linkedin_url: Optional[str] = Form(None),
    social_section_visible: Optional[str] = Form(None),
    # Quick links
    quick_links_section_visible: Optional[str] = Form(None),
    quick_links_pages: Optional[str] = Form(None),  # JSON string
    # Contact information
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    contact_address: Optional[str] = Form(None),
    contact_office_hours: Optional[str] = Form(None),
    contact_section_visible: Optional[str] = Form(None),
    # Partner section (Become a Partner)
    partner_section_visible: Optional[str] = Form(None),
    partner_section_title: Optional[str] = Form(None),
    partner_section_content: Optional[str] = Form(None),
    partner_section_button_text: Optional[str] = Form(None),
    partner_section_button_url: Optional[str] = Form(None),
    # Statistics section (Our Numbers)
    statistics_section_visible: Optional[str] = Form(None),
    statistics_section_title: Optional[str] = Form(None),
    smtp_sender_email: Optional[str] = Form(None),
    smtp_sender_password: Optional[str] = Form(None),
    smtp_host: Optional[str] = Form(None),
    smtp_port: Optional[str] = Form(None),
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
        'hero_layout_direction': hero_layout_direction if hero_layout_direction else None,
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
        # SMTP server configuration
        'smtp_sender_email': smtp_sender_email,
        'smtp_sender_password': smtp_sender_password,
        'smtp_host': smtp_host,
        'smtp_port': int(smtp_port) if smtp_port and smtp_port.strip() else None,
        'admin_panel_title': admin_panel_title,
        # Social media links
        'social_facebook_url': social_facebook_url,
        'social_twitter_url': social_twitter_url,
        'social_instagram_url': social_instagram_url,
        'social_youtube_url': social_youtube_url,
        'social_linkedin_url': social_linkedin_url,
        'social_section_visible': int(social_section_visible) if social_section_visible is not None and social_section_visible != '' else None,
        # Quick links
        'quick_links_section_visible': int(quick_links_section_visible) if (quick_links_section_visible is not None and str(quick_links_section_visible).strip() != '') else None,
        'quick_links_pages': quick_links_pages if quick_links_pages is not None else None,
        # Contact information
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'contact_address': contact_address,
        'contact_office_hours': contact_office_hours,
        'contact_section_visible': int(contact_section_visible) if contact_section_visible is not None and contact_section_visible != '' else None,
        # Partner section (Become a Partner)
        'partner_section_visible': int(partner_section_visible) if partner_section_visible is not None and partner_section_visible != '' else None,
        'partner_section_title': partner_section_title,
        'partner_section_content': partner_section_content,
        'partner_section_button_text': partner_section_button_text,
        'partner_section_button_url': partner_section_button_url,
        # Statistics section (Our Numbers)
        'statistics_section_visible': int(statistics_section_visible) if statistics_section_visible is not None and statistics_section_visible != '' else None,
        'statistics_section_title': statistics_section_title
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
        # Always update if value is provided (including empty strings and '0' for visibility flags)
        if value is not None:
            # Handle empty strings for URL fields - convert to None
            if isinstance(value, str) and value == '' and key.endswith('_url'):
                setattr(settings, key, None)
            # Handle quick_links_pages - ensure it's a valid JSON string
            elif key == 'quick_links_pages':
                # If it's an empty string, set to empty JSON array
                if value == '':
                    setattr(settings, key, '[]')
                else:
                    # Validate it's valid JSON, if not, set to empty array
                    try:
                        import json
                        json.loads(value)  # Validate JSON
                        setattr(settings, key, value)
                    except (json.JSONDecodeError, TypeError):
                        setattr(settings, key, '[]')
            # For visibility flags (including quick_links_section_visible), ensure 0 is saved
            elif key == 'quick_links_section_visible' or key == 'social_section_visible' or key == 'contact_section_visible' or key == 'partner_section_visible' or key == 'statistics_section_visible':
                # Explicitly set the value (0 or 1) - value is already int from update_fields dict
                # Ensure we save 0 when checkbox is unchecked
                setattr(settings, key, int(value) if value is not None else 0)
            elif key.endswith('_section_visible') or key.endswith('_visible'):
                # Explicitly set the value (0 or 1) - don't skip 0
                setattr(settings, key, value)
            else:
                setattr(settings, key, value)
    
    # Update .env file with SMTP settings if they were provided
    if smtp_sender_email is not None or smtp_sender_password is not None or smtp_host is not None or smtp_port is not None:
        try:
            update_env_file(
                smtp_sender_email=smtp_sender_email if smtp_sender_email else None,
                smtp_sender_password=smtp_sender_password if smtp_sender_password else None,
                smtp_host=smtp_host if smtp_host else None,
                smtp_port=int(smtp_port) if smtp_port and smtp_port.strip() else None
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to update .env file: {e}")
    
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

# ============ PAGE ROUTING HELPER ============
# Maps page names to their corresponding models and schemas
PAGE_ROUTING = {
    'home': {'model': HomePage, 'create': HomePageCreate, 'update': HomePageUpdate, 'response': HomePageResponse},
    'index': {'model': HomePage, 'create': HomePageCreate, 'update': HomePageUpdate, 'response': HomePageResponse},
    'about': {'model': About, 'create': AboutCreate, 'update': AboutUpdate, 'response': AboutResponse},
    'contact': {'model': ContactPage, 'create': ContactPageCreate, 'update': ContactPageUpdate, 'response': ContactPageResponse},
    'blog': {'model': BlogPage, 'create': BlogPageCreate, 'update': BlogPageUpdate, 'response': BlogPageResponse},
    'gallery': {'model': GalleryPage, 'create': GalleryPageCreate, 'update': GalleryPageUpdate, 'response': GalleryPageResponse},
    'branches': {'model': BranchesPage, 'create': BranchesPageCreate, 'update': BranchesPageUpdate, 'response': BranchesPageResponse},
    'departments': {'model': DepartmentsPage, 'create': DepartmentsPageCreate, 'update': DepartmentsPageUpdate, 'response': DepartmentsPageResponse},
    'events': {'model': EventsPage, 'create': EventsPageCreate, 'update': EventsPageUpdate, 'response': EventsPageResponse},
    'documents': {'model': DocumentsPage, 'create': DocumentsPageCreate, 'update': DocumentsPageUpdate, 'response': DocumentsPageResponse},
}

def get_page_config(page_name: str):
    """Get the model and schema configuration for a page name"""
    normalized_name = page_name.lower().replace('_', '-')
    if normalized_name in PAGE_ROUTING:
        return PAGE_ROUTING[normalized_name]
    raise HTTPException(status_code=404, detail=f"Page type '{page_name}' not found")

# ============ PAGES ENDPOINTS ============
@app.get("/api/pages/{page_name}")
def get_page(page_name: str, include_draft: bool = False, db: Session = Depends(get_db)):
    """Get a page by name (public endpoint, only returns published unless include_draft=True)"""
    try:
        config = get_page_config(page_name)
        model = config['model']
        response_schema = config['response']
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"Page type '{page_name}' not found")
    
    # Query the appropriate table (each table should only have one row)
    page = db.query(model).first()
    
    # Helper function to get default page data
    def get_default_page_data():
        default_data = {
            'id': 0,  # Indicates it doesn't exist yet
            'is_published': 0 if include_draft else 1,  # For public, show as published (empty)
            'title': page_name.capitalize(),
            'page_header_title': page_name.capitalize(),
            'page_header_subtitle': None,
            'page_header_visible': 1,
        }
        # Add page-specific defaults based on model
        if model == HomePage:
            default_data.update({
                'news_section_visible': 1,
                'partner_section_visible': 1,
                'events_section_visible': 1,
                'statistics_section_visible': 1,
                'partners_faith_section_visible': 1,
                'testimonials_section_visible': 1,
                'latest_news_section_visible': 1,
                'newsletter_section_visible': 1,
            })
        elif model == About:
            default_data.update({
                'history_visible': 1,
                'mission_visible': 1,
                'vision_visible': 1,
                'values_visible': 1,
                'institutions_visible': 1,
                'content1_visible': 1,
                'content1_label': 'Content 1',
                'content2_visible': 1,
                'content2_label': 'Content 2',
                'content3_visible': 1,
                'content3_label': 'Content 3',
            })
        elif model == ContactPage:
            default_data.update({
                'contact_info_section_visible': 1,
                'contact_form_section_visible': 1,
                'contact_partner_section_visible': 1,
            })
        elif model == BlogPage:
            default_data.update({
                'blog_content_section_visible': 1,
                'blog_sidebar_section_visible': 1,
                'blog_recent_posts_section_visible': 1,
                'blog_categories_section_visible': 1,
                'blog_newsletter_section_visible': 1,
            })
        elif model == GalleryPage:
            default_data.update({
                'gallery_filter_section_visible': 1,
                'gallery_content_section_visible': 1,
            })
        elif model == BranchesPage:
            default_data.update({
                'branches_content_section_visible': 1,
            })
        elif model == DepartmentsPage:
            default_data.update({
                'departments_content_section_visible': 1,
            })
        elif model == EventsPage:
            default_data.update({
                'events_content_section_visible': 1,
            })
        elif model == DocumentsPage:
            default_data.update({
                'documents_content_section_visible': 1,
            })
        return default_data
    
    # If page doesn't exist
    if not page:
        if include_draft:
            # Return a default dict for admin to edit
            return get_default_page_data()
        else:
            # Public endpoint - return default empty page (not 404)
            return get_default_page_data()
    
    # Only return published pages to public, unless explicitly requesting draft
    if not include_draft and page.is_published == 0:
        # Return default empty page instead of 404 for public access
        return get_default_page_data()
    
    return page

@app.get("/api/pages/drafts/count")
def get_drafts_count(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get count of unpublished pages (Admin only)"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    count = 0
    for page_name, config in PAGE_ROUTING.items():
        model = config['model']
        count += db.query(model).filter(model.is_published == 0).count()
    return {"count": count}

def update_html_sections(page_name: str, page_data: Dict):
    """Update specific sections in HTML file using regex, without replacing entire file"""
    try:
        # Get the project root directory
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file)
        root_dir = os.path.dirname(backend_dir)
        
        # Construct file path
        filename = f"{page_name}.html"
        if page_name == 'index' or page_name == 'home':
            filename = "index.html"
        file_path = os.path.join(root_dir, filename)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"HTML file {filename} not found, skipping HTML update")
            return
        
        # Read HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        original_content = html_content
        updated = False
        
        # Escape HTML special characters for regex
        def escape_html(text):
            if not text:
                return ''
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#039;'))
        
        # Update page header title
        if 'page_header_title' in page_data and page_data['page_header_title']:
            # Match: <h1>...</h1> inside .page-header
            pattern = r'(<section[^>]*class="[^"]*page-header[^"]*"[^>]*>.*?<h1[^>]*>)(.*?)(</h1>)'
            replacement = r'\1' + escape_html(page_data['page_header_title']) + r'\3'
            new_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
            if new_content != html_content:
                html_content = new_content
                updated = True
        
        # Update page header subtitle
        if 'page_header_subtitle' in page_data and page_data['page_header_subtitle']:
            # Match: <p class="lead">...</p> inside .page-header
            pattern = r'(<section[^>]*class="[^"]*page-header[^"]*"[^>]*>.*?<p[^>]*class="[^"]*lead[^"]*"[^>]*>)(.*?)(</p>)'
            replacement = r'\1' + escape_html(page_data['page_header_subtitle']) + r'\3'
            new_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
            if new_content != html_content:
                html_content = new_content
                updated = True
        
        # Update data-field attributes (for structured content)
        data_fields = ['history', 'mission', 'vision', 'values', 'institutions', 'content1', 'content2', 'content3']
        for field in data_fields:
            if field in page_data and page_data[field] is not None:
                value = str(page_data[field])
                # Convert newlines to <br> tags for HTML content
                formatted_value = value.replace('\n', '<br>')
                # Escape HTML but preserve <br> tags
                formatted_value = escape_html(formatted_value).replace('&lt;br&gt;', '<br>')
                
                # Match: <div data-field="field_name">...</div> or <p data-field="field_name">...</p>
                pattern = rf'(<[^>]+data-field=["\']?{re.escape(field)}["\']?[^>]*>)(.*?)(</[^>]+>)'
                replacement = r'\1' + formatted_value + r'\3'
                new_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
                if new_content != html_content:
                    html_content = new_content
                    updated = True
        
        # Update content labels (h2/h3 inside data-field containers)
        for field in ['content1', 'content2', 'content3']:
            label_field = f'{field}_label'
            if label_field in page_data and page_data[label_field] is not None:
                value = escape_html(page_data[label_field])
                # Match: <h2> or <h3> inside data-field container
                pattern = rf'(<[^>]+data-field=["\']?{re.escape(field)}["\']?[^>]*>.*?<h[23][^>]*>)(.*?)(</h[23]>)'
                replacement = r'\1' + value + r'\3'
                new_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
                if new_content != html_content:
                    html_content = new_content
                    updated = True
        
        # Only write if something was updated
        if updated and html_content != original_content:
            # Create backup
            backup_path = file_path + '.backup'
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
            
            # Write updated HTML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Updated HTML sections in {filename}")
        else:
            print(f"No matching sections found to update in {filename}")
            
    except Exception as e:
        print(f"Error updating HTML sections for {page_name}: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise exception, just log it

@app.put("/api/pages/{page_name}")
def update_page(page_name: str, page_data: dict, publish: bool = False, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Update a page by name (Admin only). Use publish=True to publish, False to save as draft"""
    check_permission(current_user, "write")
    
    try:
        config = get_page_config(page_name)
        model = config['model']
        update_schema = config['update']
        response_schema = config['response']
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"Page '{page_name}' not found")
    
    # Get or create the page (each table should only have one row)
    db_page = db.query(model).first()
    if not db_page:
        # Create if doesn't exist
        # Filter out fields that don't exist in the model (like page_name, id)
        create_data = {k: v for k, v in page_data.items() if v is not None}
        # Remove fields that are not model attributes
        model_columns = {col.name for col in model.__table__.columns}
        create_data = {k: v for k, v in create_data.items() if k in model_columns}
        create_data['is_published'] = 0
        if 'created_by' in model_columns:
            create_data['created_by'] = current_user["user_id"]
        if 'updated_by' in model_columns:
            create_data['updated_by'] = current_user["user_id"]
        db_page = model(**create_data)
        db.add(db_page)
    else:
        # Update existing - validate with schema
        try:
            validated_data = update_schema(**page_data).dict(exclude_unset=True, exclude_none=False)
        except Exception as e:
            # If schema validation fails, use raw data (for backward compatibility)
            validated_data = {k: v for k, v in page_data.items() if v is not None}
        
        # Filter out fields that don't exist in the model (like page_name, id)
        model_columns = {col.name for col in model.__table__.columns}
        validated_data = {k: v for k, v in validated_data.items() if k in model_columns}
        
        # Update all fields
        for key, value in validated_data.items():
            if hasattr(db_page, key):
                if value is not None:
                    setattr(db_page, key, value)
        
        # Handle publish status
        if publish:
            db_page.is_published = 1
            db_page.published_at = datetime.now()
        elif "is_published" in validated_data:
            if validated_data["is_published"] == 1:
                db_page.is_published = 1
                db_page.published_at = datetime.now()
            else:
                db_page.is_published = 0
        
        db_page.updated_by = current_user["user_id"]
    
    db.commit()
    db.refresh(db_page)
    
    # Update HTML file with structured data (only update specific sections, not entire file)
    try:
        update_html_sections(page_name, validated_data if db_page else create_data)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not update HTML file for {page_name}: {e}")
        import traceback
        traceback.print_exc()
    
    return db_page

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

# About Content Endpoints (using About model)
@app.get("/api/about-content", response_model=AboutResponse)
def get_about_content(db: Session = Depends(get_db)):
    """Get about page content (public endpoint) - uses About model"""
    about_content = db.query(About).first()
    if not about_content:
        # Return default if none exists
        return AboutResponse(
            id=0,
            title="About Us",
            page_header_title="About Us",
            page_header_subtitle=None,
            page_header_visible=1,
            history=None,
            history_visible=1,
            mission=None,
            mission_visible=1,
            vision=None,
            vision_visible=1,
            values=None,
            values_visible=1,
            institutions=None,
            institutions_visible=1,
            content1=None,
            content1_visible=1,
            content1_label="Content 1",
            content2=None,
            content2_visible=1,
            content2_label="Content 2",
            content3=None,
            content3_visible=1,
            content3_label="Content 3",
            is_published=1,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return about_content

@app.get("/api/about-content/admin", response_model=AboutResponse)
def get_about_content_admin(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get about page content (admin endpoint) - uses About model"""
    about_content = db.query(About).first()
    if not about_content:
        raise HTTPException(status_code=404, detail="About content not found")
    return about_content

@app.post("/api/about-content", response_model=AboutResponse)
def create_about_content(
    about_content: AboutCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create about page content (admin only) - uses About model"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    
    # Check if content already exists
    existing = db.query(About).first()
    if existing:
        raise HTTPException(status_code=400, detail="About content already exists. Use PUT to update.")
    
    create_data = about_content.dict(exclude_unset=True)
    create_data['created_by'] = current_user["user_id"]
    create_data['updated_by'] = current_user["user_id"]
    
    db_about = About(**create_data)
    db.add(db_about)
    db.commit()
    db.refresh(db_about)
    return db_about

@app.put("/api/about-content", response_model=AboutResponse)
def update_about_content(
    about_content: AboutUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update about page content (admin only) - uses About model"""
    require_role(current_user, CONTRIBUTORS_ROLES)
    
    db_about = db.query(About).first()
    if not db_about:
        # Create if doesn't exist
        create_data = about_content.dict(exclude_unset=True)
        create_data['created_by'] = current_user["user_id"]
        create_data['updated_by'] = current_user["user_id"]
        if 'title' not in create_data or not create_data['title']:
            create_data['title'] = "About Us"
        db_about = About(**create_data)
        db.add(db_about)
    else:
        # Update existing
        update_data = about_content.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_about, key):
                setattr(db_about, key, value)
        db_about.updated_by = current_user["user_id"]
        db_about.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_about)
    return db_about

# ============ HOME PAGE ENDPOINTS ============
@app.get("/api/home", response_model=HomePageResponse)
def get_home(db: Session = Depends(get_db)):
    """Get home page content"""
    home = db.query(HomePage).first()
    if not home:
        # Return default/empty home if none exists
        return HomePageResponse(
            id=0,
            title="Home",
            page_header_title=None,
            page_header_subtitle=None,
            page_header_visible=1,
            news_section_title="News",
            news_section_visible=1,
            partner_section_title="Become a Partner",
            partner_section_content=None,
            partner_section_button_text="Partner With Us",
            partner_section_button_url="contact.html",
            partner_section_visible=1,
            events_section_title="OUR EVENTS",
            events_section_visible=1,
            statistics_section_title="OUR NUMBERS",
            statistics_section_visible=1,
            partners_faith_section_title="PARTNERS IN FAITH",
            partners_faith_section_visible=1,
            testimonials_section_visible=1,
            testimonial1_title=None,
            testimonial1_content=None,
            testimonial1_author=None,
            testimonial1_visible=1,
            testimonial2_title=None,
            testimonial2_content=None,
            testimonial2_author=None,
            testimonial2_visible=1,
            latest_news_section_title="Latest News",
            latest_news_section_visible=1,
            newsletter_section_title="Newsletter",
            newsletter_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return home

@app.post("/api/home", response_model=HomePageResponse)
def create_home(home: HomePageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create home page content (Admin only)"""
    # Check if home already exists
    existing = db.query(HomePage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Home page content already exists. Use PUT to update.")
    
    db_home = HomePage(**home.dict())
    db.add(db_home)
    db.commit()
    db.refresh(db_home)
    return db_home

@app.put("/api/home", response_model=HomePageResponse)
def update_home(home: HomePageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update home page content (Admin only)"""
    db_home = db.query(HomePage).first()
    if not db_home:
        # Create if doesn't exist
        create_data = home.dict(exclude_unset=True)
        db_home = HomePage(**create_data)
        db.add(db_home)
    else:
        # Update existing
        update_data = home.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_home, key, value)
    
    db.commit()
    db.refresh(db_home)
    return db_home

# ============ CONTACT PAGE ENDPOINTS ============
@app.get("/api/contact-page", response_model=ContactPageResponse)
def get_contact_page(db: Session = Depends(get_db)):
    """Get contact page content"""
    contact_page = db.query(ContactPage).first()
    if not contact_page:
        # Return default/empty contact page if none exists
        return ContactPageResponse(
            id=0,
            title="Contact",
            page_header_title="Contact Us",
            page_header_subtitle="Get in Touch",
            page_header_visible=1,
            contact_info_section_visible=1,
            contact_form_section_visible=1,
            contact_partner_section_visible=1,
            contact_partner_title=None,
            contact_partner_content=None,
            contact_partner_button_text=None,
            contact_partner_button_url=None,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return contact_page

@app.post("/api/contact-page", response_model=ContactPageResponse)
def create_contact_page(contact_page: ContactPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create contact page content (Admin only)"""
    # Check if contact page already exists
    existing = db.query(ContactPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contact page content already exists. Use PUT to update.")
    
    db_contact_page = ContactPage(**contact_page.dict())
    db.add(db_contact_page)
    db.commit()
    db.refresh(db_contact_page)
    return db_contact_page

@app.put("/api/contact-page", response_model=ContactPageResponse)
def update_contact_page(contact_page: ContactPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update contact page content (Admin only)"""
    db_contact_page = db.query(ContactPage).first()
    if not db_contact_page:
        # Create if doesn't exist
        create_data = contact_page.dict(exclude_unset=True)
        db_contact_page = ContactPage(**create_data)
        db.add(db_contact_page)
    else:
        # Update existing
        update_data = contact_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_contact_page, key, value)
    
    db.commit()
    db.refresh(db_contact_page)
    return db_contact_page

# ============ BLOG PAGE ENDPOINTS ============
@app.get("/api/blog-page", response_model=BlogPageResponse)
def get_blog_page(db: Session = Depends(get_db)):
    """Get blog page content"""
    blog_page = db.query(BlogPage).first()
    if not blog_page:
        # Return default/empty blog page if none exists
        return BlogPageResponse(
            id=0,
            title="Blog",
            page_header_title="Blog",
            page_header_subtitle="Latest News & Updates",
            page_header_visible=1,
            blog_content_section_visible=1,
            blog_sidebar_section_visible=1,
            blog_recent_posts_section_visible=1,
            blog_categories_section_visible=1,
            blog_newsletter_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return blog_page

@app.post("/api/blog-page", response_model=BlogPageResponse)
def create_blog_page(blog_page: BlogPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create blog page content (Admin only)"""
    # Check if blog page already exists
    existing = db.query(BlogPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Blog page content already exists. Use PUT to update.")
    
    db_blog_page = BlogPage(**blog_page.dict())
    db.add(db_blog_page)
    db.commit()
    db.refresh(db_blog_page)
    return db_blog_page

@app.put("/api/blog-page", response_model=BlogPageResponse)
def update_blog_page(blog_page: BlogPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update blog page content (Admin only)"""
    db_blog_page = db.query(BlogPage).first()
    if not db_blog_page:
        # Create if doesn't exist
        create_data = blog_page.dict(exclude_unset=True)
        db_blog_page = BlogPage(**create_data)
        db.add(db_blog_page)
    else:
        # Update existing
        update_data = blog_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_blog_page, key, value)
    
    db.commit()
    db.refresh(db_blog_page)
    return db_blog_page

# ============ GALLERY PAGE ENDPOINTS ============
@app.get("/api/gallery-page", response_model=GalleryPageResponse)
def get_gallery_page(db: Session = Depends(get_db)):
    """Get gallery page content"""
    gallery_page = db.query(GalleryPage).first()
    if not gallery_page:
        # Return default/empty gallery page if none exists
        return GalleryPageResponse(
            id=0,
            title="Gallery",
            page_header_title="Gallery",
            page_header_subtitle="Our Church in Pictures",
            page_header_visible=1,
            gallery_filter_section_visible=1,
            gallery_content_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return gallery_page

@app.post("/api/gallery-page", response_model=GalleryPageResponse)
def create_gallery_page(gallery_page: GalleryPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create gallery page content (Admin only)"""
    # Check if gallery page already exists
    existing = db.query(GalleryPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Gallery page content already exists. Use PUT to update.")
    
    db_gallery_page = GalleryPage(**gallery_page.dict())
    db.add(db_gallery_page)
    db.commit()
    db.refresh(db_gallery_page)
    return db_gallery_page

@app.put("/api/gallery-page", response_model=GalleryPageResponse)
def update_gallery_page(gallery_page: GalleryPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update gallery page content (Admin only)"""
    db_gallery_page = db.query(GalleryPage).first()
    if not db_gallery_page:
        # Create if doesn't exist
        create_data = gallery_page.dict(exclude_unset=True)
        db_gallery_page = GalleryPage(**create_data)
        db.add(db_gallery_page)
    else:
        # Update existing
        update_data = gallery_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_gallery_page, key, value)
    
    db.commit()
    db.refresh(db_gallery_page)
    return db_gallery_page

# ============ BRANCHES PAGE ENDPOINTS ============
@app.get("/api/branches-page", response_model=BranchesPageResponse)
def get_branches_page(db: Session = Depends(get_db)):
    """Get branches page content"""
    branches_page = db.query(BranchesPage).first()
    if not branches_page:
        # Return default/empty branches page if none exists
        return BranchesPageResponse(
            id=0,
            title="Branches",
            page_header_title="Branches",
            page_header_subtitle="Our Regional Offices",
            page_header_visible=1,
            branches_content_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return branches_page

@app.post("/api/branches-page", response_model=BranchesPageResponse)
def create_branches_page(branches_page: BranchesPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create branches page content (Admin only)"""
    # Check if branches page already exists
    existing = db.query(BranchesPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Branches page content already exists. Use PUT to update.")
    
    db_branches_page = BranchesPage(**branches_page.dict())
    db.add(db_branches_page)
    db.commit()
    db.refresh(db_branches_page)
    return db_branches_page

@app.put("/api/branches-page", response_model=BranchesPageResponse)
def update_branches_page(branches_page: BranchesPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update branches page content (Admin only)"""
    db_branches_page = db.query(BranchesPage).first()
    if not db_branches_page:
        # Create if doesn't exist
        create_data = branches_page.dict(exclude_unset=True)
        db_branches_page = BranchesPage(**create_data)
        db.add(db_branches_page)
    else:
        # Update existing
        update_data = branches_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_branches_page, key, value)
    
    db.commit()
    db.refresh(db_branches_page)
    return db_branches_page

# ============ DEPARTMENTS PAGE ENDPOINTS ============
@app.get("/api/departments-page", response_model=DepartmentsPageResponse)
def get_departments_page(db: Session = Depends(get_db)):
    """Get departments page content"""
    departments_page = db.query(DepartmentsPage).first()
    if not departments_page:
        # Return default/empty departments page if none exists
        return DepartmentsPageResponse(
            id=0,
            title="Departments",
            page_header_title="Departments",
            page_header_subtitle="Our Organizational Structure",
            page_header_visible=1,
            departments_content_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return departments_page

@app.post("/api/departments-page", response_model=DepartmentsPageResponse)
def create_departments_page(departments_page: DepartmentsPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create departments page content (Admin only)"""
    # Check if departments page already exists
    existing = db.query(DepartmentsPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Departments page content already exists. Use PUT to update.")
    
    db_departments_page = DepartmentsPage(**departments_page.dict())
    db.add(db_departments_page)
    db.commit()
    db.refresh(db_departments_page)
    return db_departments_page

@app.put("/api/departments-page", response_model=DepartmentsPageResponse)
def update_departments_page(departments_page: DepartmentsPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update departments page content (Admin only)"""
    db_departments_page = db.query(DepartmentsPage).first()
    if not db_departments_page:
        # Create if doesn't exist
        create_data = departments_page.dict(exclude_unset=True)
        db_departments_page = DepartmentsPage(**create_data)
        db.add(db_departments_page)
    else:
        # Update existing
        update_data = departments_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_departments_page, key, value)
    
    db.commit()
    db.refresh(db_departments_page)
    return db_departments_page

# ============ EVENTS PAGE ENDPOINTS ============
@app.get("/api/events-page", response_model=EventsPageResponse)
def get_events_page(db: Session = Depends(get_db)):
    """Get events page content"""
    events_page = db.query(EventsPage).first()
    if not events_page:
        # Return default/empty events page if none exists
        return EventsPageResponse(
            id=0,
            title="Events",
            page_header_title="Our Events",
            page_header_subtitle="Stay updated with our upcoming events and activities",
            page_header_visible=1,
            events_content_section_visible=1,
            is_published=0,
            published_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )
    return events_page

@app.post("/api/events-page", response_model=EventsPageResponse)
def create_events_page(events_page: EventsPageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Create events page content (Admin only)"""
    # Check if events page already exists
    existing = db.query(EventsPage).first()
    if existing:
        raise HTTPException(status_code=400, detail="Events page content already exists. Use PUT to update.")
    
    db_events_page = EventsPage(**events_page.dict())
    db.add(db_events_page)
    db.commit()
    db.refresh(db_events_page)
    return db_events_page

@app.put("/api/events-page", response_model=EventsPageResponse)
def update_events_page(events_page: EventsPageUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Update events page content (Admin only)"""
    db_events_page = db.query(EventsPage).first()
    if not db_events_page:
        # Create if doesn't exist
        create_data = events_page.dict(exclude_unset=True)
        db_events_page = EventsPage(**create_data)
        db.add(db_events_page)
    else:
        # Update existing
        update_data = events_page.dict(exclude_unset=True, exclude_none=False)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_events_page, key, value)
    
    db.commit()
    db.refresh(db_events_page)
    return db_events_page

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

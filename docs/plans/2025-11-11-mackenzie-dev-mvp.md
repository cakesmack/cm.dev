# Mackenzie-Dev MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a unified portfolio & business management system that combines dynamic portfolio CMS, CRM (leads/clients), and invoicing with a beautiful TailwindCSS interface.

**Architecture:** FastAPI backend with Jinja2 templating, SQLAlchemy ORM, JWT authentication with RBAC. Frontend uses existing TailwindCSS aesthetic with server-rendered templates enhanced by vanilla JavaScript. Starting fresh database (no data migration needed).

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Jinja2, TailwindCSS, PostgreSQL/SQLite, JWT (python-jose), Passlib

---

## Phase 1: Project Foundation & Authentication

### Task 1: Initialize Project Structure

**Files:**
- Create: `cm.dev/backend/app/__init__.py`
- Create: `cm.dev/backend/app/main.py`
- Create: `cm.dev/backend/app/db.py`
- Create: `cm.dev/backend/app/core/__init__.py`
- Create: `cm.dev/backend/app/core/config.py`
- Create: `cm.dev/backend/requirements.txt`
- Create: `cm.dev/backend/.env.example`
- Create: `cm.dev/backend/.gitignore`

**Step 1: Create directory structure**

```bash
cd cm.dev
mkdir -p backend/app/core backend/app/models backend/app/schemas backend/app/routers backend/app/routers/admin backend/app/services backend/app/templates/public backend/app/templates/admin backend/app/templates/components backend/static/css backend/static/js backend/static/uploads backend/tests alembic
```

**Step 2: Create requirements.txt**

Create `backend/requirements.txt`:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
jinja2==3.1.2
aiofiles==23.2.1
```

**Step 3: Create .env.example**

Create `backend/.env.example`:

```
DATABASE_URL=sqlite:///./mackenzie_dev.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

**Step 4: Create .gitignore**

Create `backend/.gitignore`:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
.env
*.db
*.sqlite
*.sqlite3
.DS_Store
.vscode/
.idea/
*.log
/static/uploads/*
!/static/uploads/.gitkeep
alembic/versions/*
!alembic/versions/.gitkeep
```

**Step 5: Create core config**

Create `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mackenzie-Dev"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./mackenzie_dev.db"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

**Step 6: Create database setup**

Create `backend/app/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 7: Create main FastAPI app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}
```

**Step 8: Create empty __init__.py files**

```bash
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/routers/admin/__init__.py
touch backend/app/services/__init__.py
touch backend/tests/__init__.py
```

**Step 9: Create .gitkeep files for empty directories**

```bash
touch backend/static/uploads/.gitkeep
touch backend/alembic/versions/.gitkeep
```

**Step 10: Test the basic setup**

Run from `cm.dev/backend`:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Expected: Server starts on http://127.0.0.1:8000, visiting /health returns `{"status": "healthy", "version": "1.0.0"}`

**Step 11: Commit**

```bash
git init
git add .
git commit -m "feat: initialize project structure and basic FastAPI app"
```

---

### Task 2: Database Models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/client.py`
- Create: `backend/app/models/lead.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/models/invoice.py`
- Modify: `backend/app/models/__init__.py`

**Step 1: Create User model**

Create `backend/app/models/user.py`:

```python
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class User(Base):
    """Admin user (business owner - you)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    role = Column(String, default="admin", nullable=False)  # Only 'admin' for MVP
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")
```

**Step 2: Create Client model**

Create `backend/app/models/client.py`:

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Client(Base):
    """Client/customer of the business"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String, nullable=True)
    contact_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    tax_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")
```

**Step 3: Create Lead model**

Create `backend/app/models/lead.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from datetime import datetime
import enum
from app.db import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class Lead(Base):
    """Lead from contact form submissions"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String, default="Contact Form", nullable=False)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
```

**Step 4: Create Project model**

Create `backend/app/models/project.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Project(Base):
    """Portfolio project"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)  # Short description
    case_study = Column(Text, nullable=True)  # Long markdown content
    tech_stack = Column(JSON, nullable=True)  # List of technologies
    project_url = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    is_published = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media = relationship("ProjectMedia", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project")


class ProjectMedia(Base):
    """Media files for projects"""
    __tablename__ = "project_media"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    media_type = Column(String, default="image", nullable=False)  # image, video
    url = Column(String, nullable=False)
    alt_text = Column(String, nullable=True)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="media")
```

**Step 5: Create Invoice models**

Create `backend/app/models/invoice.py`:

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from decimal import Decimal
import enum
from app.db import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    """Invoice"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    invoice_number = Column(String, nullable=False, unique=True, index=True)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    currency = Column(String, default="USD", nullable=False)

    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)

    subtotal = Column(Numeric(10, 2), default=Decimal("0.00"))
    tax_rate = Column(Numeric(5, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(10, 2), default=Decimal("0.00"))
    total = Column(Numeric(10, 2), default=Decimal("0.00"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    """Invoice line item"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

    @hybrid_property
    def total(self):
        return self.quantity * self.unit_price
```

**Step 6: Update models __init__.py**

Modify `backend/app/models/__init__.py`:

```python
from app.models.user import User
from app.models.client import Client
from app.models.lead import Lead, LeadStatus
from app.models.project import Project, ProjectMedia
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus

__all__ = [
    "User",
    "Client",
    "Lead",
    "LeadStatus",
    "Project",
    "ProjectMedia",
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
]
```

**Step 7: Initialize Alembic**

```bash
cd backend
alembic init alembic
```

**Step 8: Configure Alembic**

Modify `backend/alembic/env.py` - find the line `target_metadata = None` and replace with:

```python
from app.db import Base
from app.models import *  # Import all models
target_metadata = Base.metadata
```

Also in `alembic/env.py`, add at top after imports:

```python
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

**Step 9: Create initial migration**

```bash
alembic revision --autogenerate -m "Initial schema"
```

Expected: Creates a new migration file in `alembic/versions/`

**Step 10: Run migration**

```bash
alembic upgrade head
```

Expected: Creates all tables in database

**Step 11: Verify database**

Start uvicorn and check that no errors occur:
```bash
uvicorn app.main:app --reload
```

**Step 12: Commit**

```bash
git add .
git commit -m "feat: add database models and migrations"
```

---

### Task 3: Authentication & Security

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/dependencies.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`

**Step 1: Create security utilities**

Create `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 2: Create RBAC dependencies**

Create `backend/app/core/dependencies.py`:

```python
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

**Step 3: Create auth schemas**

Create `backend/app/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

**Step 4: Create user schemas**

Create `backend/app/schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 5: Create auth router**

Create `backend/app/routers/auth.py`:

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

**Step 6: Include auth router in main app**

Modify `backend/app/main.py`, add after templates setup:

```python
from app.routers import auth

app.include_router(auth.router, prefix=settings.API_PREFIX)
```

**Step 7: Add __init__.py for schemas**

```bash
touch backend/app/schemas/__init__.py
```

**Step 8: Create admin user script**

Create `backend/create_admin.py`:

```python
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
import sys

# Create tables
Base.metadata.create_all(bind=engine)

def create_admin_user(email: str, password: str, full_name: str, company_name: str):
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return

        # Create admin user
        hashed_password = get_password_hash(password)
        admin = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            company_name=company_name,
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created successfully! ID: {admin.id}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <email> <password> <full_name> [company_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    company_name = sys.argv[4] if len(sys.argv) > 4 else None

    create_admin_user(email, password, full_name, company_name)
```

**Step 9: Create admin user**

```bash
cd backend
python create_admin.py "craig@mackenzie.dev" "changeme123" "Craig Mackenzie" "Mackenzie-Dev"
```

Expected: "Admin user created successfully! ID: 1"

**Step 10: Test authentication**

Start server:
```bash
uvicorn app.main:app --reload
```

Test login with curl or API docs at http://127.0.0.1:8000/api/docs:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=craig@mackenzie.dev&password=changeme123"
```

Expected: Returns JSON with `access_token` and `token_type: "bearer"`

**Step 11: Commit**

```bash
git add .
git commit -m "feat: add JWT authentication and RBAC"
```

---

## Phase 2: Portfolio CMS (Admin Backend)

### Task 4: Project CRUD API

**Files:**
- Create: `backend/app/schemas/project.py`
- Create: `backend/app/services/project_service.py`
- Create: `backend/app/routers/admin/projects.py`
- Modify: `backend/app/main.py`

**Step 1: Create project schemas**

Create `backend/app/schemas/project.py`:

```python
from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List
import re


class ProjectMediaBase(BaseModel):
    media_type: str = "image"
    url: str
    alt_text: Optional[str] = None
    display_order: int = 0


class ProjectMediaCreate(ProjectMediaBase):
    pass


class ProjectMediaResponse(ProjectMediaBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    description: str
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[date] = None
    is_published: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[date] = None
    is_published: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    media: List[ProjectMediaResponse] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    is_published: bool
    date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 2: Create project service**

Create `backend/app/services/project_service.py`:

```python
import re
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMedia
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import List, Optional


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


def ensure_unique_slug(db: Session, slug: str, project_id: Optional[int] = None) -> str:
    """Ensure slug is unique by appending number if needed"""
    original_slug = slug
    counter = 1

    while True:
        query = db.query(Project).filter(Project.slug == slug)
        if project_id:
            query = query.filter(Project.id != project_id)

        if not query.first():
            return slug

        slug = f"{original_slug}-{counter}"
        counter += 1


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """Create a new project"""
    slug = generate_slug(project_data.title)
    slug = ensure_unique_slug(db, slug)

    project = Project(
        **project_data.model_dump(),
        slug=slug
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_by_slug(db: Session, slug: str) -> Optional[Project]:
    """Get project by slug"""
    return db.query(Project).filter(Project.slug == slug).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100, published_only: bool = False) -> List[Project]:
    """Get list of projects"""
    query = db.query(Project)
    if published_only:
        query = query.filter(Project.is_published == True)
    return query.order_by(Project.date.desc()).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
    """Update a project"""
    project = get_project(db, project_id)
    if not project:
        return None

    update_data = project_data.model_dump(exclude_unset=True)

    # Regenerate slug if title changed
    if "title" in update_data:
        new_slug = generate_slug(update_data["title"])
        new_slug = ensure_unique_slug(db, new_slug, project_id)
        update_data["slug"] = new_slug

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project"""
    project = get_project(db, project_id)
    if not project:
        return False

    db.delete(project)
    db.commit()
    return True
```

**Step 3: Create projects admin router**

Create `backend/app/routers/admin/projects.py`:

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services import project_service

router = APIRouter(prefix="/admin/projects", tags=["admin-projects"])


@router.get("", response_model=List[ProjectListResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all projects (admin only)"""
    projects = project_service.get_projects(db, skip=skip, limit=limit, published_only=False)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific project (admin only)"""
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new project (admin only)"""
    project = project_service.create_project(db, project_data)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a project (admin only)"""
    project = project_service.update_project(db, project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a project (admin only)"""
    success = project_service.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
```

**Step 4: Create services __init__.py**

Create `backend/app/services/__init__.py`:

```python
from app.services import project_service

__all__ = ["project_service"]
```

**Step 5: Include projects router in main app**

Modify `backend/app/main.py`, add after auth router:

```python
from app.routers.admin import projects as admin_projects

app.include_router(admin_projects.router, prefix=settings.API_PREFIX)
```

**Step 6: Test project CRUD**

Start server and test at http://127.0.0.1:8000/api/docs

1. Login to get token
2. Create a project (use "Authorize" button with token)
3. List projects
4. Update project
5. Delete project

Expected: All CRUD operations work correctly

**Step 7: Commit**

```bash
git add .
git commit -m "feat: add project CRUD API for admin"
```

---

### Task 5: Media Upload for Projects

**Files:**
- Create: `backend/app/services/media_service.py`
- Create: `backend/app/routers/admin/media.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/__init__.py`

**Step 1: Create media service**

Create `backend/app/services/media_service.py`:

```python
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMedia
from app.schemas.project import ProjectMediaCreate

UPLOAD_DIR = Path("static/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> bool:
    """Validate image file"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    return True


async def save_upload_file(file: UploadFile) -> str:
    """Save uploaded file and return URL path"""
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    # Save file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Return URL path
    return f"/static/uploads/{filename}"


def create_project_media(
    db: Session,
    project_id: int,
    url: str,
    media_type: str = "image",
    alt_text: Optional[str] = None
) -> Optional[ProjectMedia]:
    """Create project media record"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    # Get max display_order for this project
    max_order = db.query(ProjectMedia).filter(
        ProjectMedia.project_id == project_id
    ).count()

    media = ProjectMedia(
        project_id=project_id,
        media_type=media_type,
        url=url,
        alt_text=alt_text or "",
        display_order=max_order
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def delete_project_media(db: Session, media_id: int) -> bool:
    """Delete project media"""
    media = db.query(ProjectMedia).filter(ProjectMedia.id == media_id).first()
    if not media:
        return False

    # Delete file from disk
    file_path = Path("." + media.url)  # Remove leading /
    if file_path.exists():
        file_path.unlink()

    db.delete(media)
    db.commit()
    return True


def get_project_media(db: Session, project_id: int):
    """Get all media for a project"""
    return db.query(ProjectMedia).filter(
        ProjectMedia.project_id == project_id
    ).order_by(ProjectMedia.display_order).all()
```

**Step 2: Create media router**

Create `backend/app/routers/admin/media.py`:

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.project import ProjectMediaResponse
from app.services import media_service

router = APIRouter(prefix="/admin/projects", tags=["admin-media"])


@router.post("/{project_id}/media", response_model=ProjectMediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_project_media(
    project_id: int,
    file: UploadFile = File(...),
    alt_text: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload media file for a project (admin only)"""
    # Validate file
    if not media_service.validate_image(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: jpg, jpeg, png, gif, webp, svg"
        )

    # Save file
    url = await media_service.save_upload_file(file)

    # Create database record
    media = media_service.create_project_media(
        db, project_id, url, media_type="image", alt_text=alt_text
    )

    if not media:
        raise HTTPException(status_code=404, detail="Project not found")

    return media


@router.get("/{project_id}/media", response_model=List[ProjectMediaResponse])
def list_project_media(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all media for a project (admin only)"""
    media = media_service.get_project_media(db, project_id)
    return media


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete project media (admin only)"""
    success = media_service.delete_project_media(db, media_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found")
    return None
```

**Step 3: Update services __init__.py**

Modify `backend/app/services/__init__.py`:

```python
from app.services import project_service, media_service

__all__ = ["project_service", "media_service"]
```

**Step 4: Include media router in main app**

Modify `backend/app/main.py`, add after projects router:

```python
from app.routers.admin import media as admin_media

app.include_router(admin_media.router, prefix=settings.API_PREFIX)
```

**Step 5: Test media upload**

1. Start server
2. Use API docs to upload an image to a project
3. List media for the project
4. Check that file exists in `static/uploads/`
5. Delete media and verify file is removed

Expected: All media operations work correctly

**Step 6: Commit**

```bash
git add .
git commit -m "feat: add media upload for projects"
```

---

## Phase 3: Public Portfolio Frontend

### Task 6: Public Portfolio Templates

**Files:**
- Create: `backend/app/templates/base.html`
- Create: `backend/app/templates/components/navbar.html`
- Create: `backend/app/templates/public/home.html`
- Create: `backend/app/templates/public/project_detail.html`
- Create: `backend/static/css/main.css`
- Create: `backend/static/js/main.js`
- Create: `backend/app/routers/public.py`
- Modify: `backend/app/main.py`

**Step 1: Create base template**

Create `backend/app/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Craig Mackenzie - Developer{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        charcoal: '#2d3748',
                        'light-grey': '#f7fafc',
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="/static/css/main.css">
    {% block extra_head %}{% endblock %}
</head>
<body class="bg-white text-charcoal font-sans">
    {% include 'components/navbar.html' %}

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-charcoal text-white py-8 mt-20">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <p>&copy; 2025 Craig Mackenzie. All rights reserved.</p>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Step 2: Create navbar component**

Create `backend/app/templates/components/navbar.html`:

```html
<nav class="fixed w-full top-0 bg-white/90 backdrop-blur-sm z-50 border-b border-gray-200">
    <div class="max-w-6xl mx-auto px-6 py-4">
        <div class="flex justify-between items-center">
            <a href="/" class="text-2xl font-bold text-charcoal">Craig Mackenzie</a>

            <div class="hidden md:flex space-x-8">
                <a href="/#projects" class="text-charcoal hover:text-gray-600 transition">Projects</a>
                <a href="/#about" class="text-charcoal hover:text-gray-600 transition">About</a>
                <a href="/#contact" class="text-charcoal hover:text-gray-600 transition">Contact</a>
            </div>

            <button id="mobile-menu-btn" class="md:hidden">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </button>
        </div>

        <div id="mobile-menu" class="hidden md:hidden mt-4 space-y-2">
            <a href="/#projects" class="block text-charcoal hover:text-gray-600 transition">Projects</a>
            <a href="/#about" class="block text-charcoal hover:text-gray-600 transition">About</a>
            <a href="/#contact" class="block text-charcoal hover:text-gray-600 transition">Contact</a>
        </div>
    </div>
</nav>
```

**Step 3: Create home template**

Create `backend/app/templates/public/home.html`:

```html
{% extends "base.html" %}

{% block content %}
<!-- Hero Section -->
<section class="pt-32 pb-20 px-6">
    <div class="max-w-4xl mx-auto text-center opacity-0 fade-in">
        <h1 class="text-5xl md:text-6xl font-bold mb-6 text-charcoal">
            Full-Stack Developer & Designer
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            I build beautiful, functional web applications that solve real problems.
            Specializing in Python, FastAPI, and modern frontend technologies.
        </p>
        <div class="flex gap-4 justify-center">
            <a href="#projects" class="bg-charcoal text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition">
                View My Work
            </a>
            <a href="#contact" class="border-2 border-charcoal text-charcoal px-8 py-3 rounded-lg hover:bg-light-grey transition">
                Get In Touch
            </a>
        </div>
    </div>
</section>

<!-- Projects Section -->
<section id="projects" class="py-20 px-6 bg-light-grey">
    <div class="max-w-6xl mx-auto">
        <h2 class="text-4xl font-bold text-center mb-12 opacity-0 fade-in">Featured Projects</h2>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for project in projects %}
            <div class="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition opacity-0 fade-in">
                <div class="h-48 bg-gradient-to-br from-blue-400 to-purple-500">
                    {% if project.media and project.media|length > 0 %}
                    <img src="{{ project.media[0].url }}" alt="{{ project.media[0].alt_text }}" class="w-full h-full object-cover">
                    {% endif %}
                </div>
                <div class="p-6">
                    <h3 class="text-xl font-bold mb-2">{{ project.title }}</h3>
                    <p class="text-gray-600 mb-4">{{ project.description }}</p>

                    {% if project.tech_stack %}
                    <div class="flex flex-wrap gap-2 mb-4">
                        {% for tech in project.tech_stack %}
                        <span class="bg-light-grey text-charcoal text-xs px-3 py-1 rounded-full">{{ tech }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}

                    <a href="/projects/{{ project.slug }}" class="text-charcoal font-semibold hover:underline">
                        View Project →
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- About Section -->
<section id="about" class="py-20 px-6">
    <div class="max-w-4xl mx-auto opacity-0 fade-in">
        <h2 class="text-4xl font-bold mb-8">About Me</h2>
        <div class="text-lg text-gray-700 space-y-4">
            <p>
                I'm a full-stack developer with a passion for creating elegant solutions to complex problems.
                With expertise in Python, FastAPI, and modern frontend technologies, I help businesses
                build scalable web applications.
            </p>
            <p>
                When I'm not coding, you'll find me exploring new technologies, contributing to open source,
                or mentoring aspiring developers.
            </p>
        </div>

        <h3 class="text-2xl font-bold mt-12 mb-6">Skills & Technologies</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-light-grey p-4 rounded-lg text-center">Python</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">FastAPI</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">JavaScript</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">TailwindCSS</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">PostgreSQL</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">Docker</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">Git</div>
            <div class="bg-light-grey p-4 rounded-lg text-center">REST APIs</div>
        </div>
    </div>
</section>

<!-- Contact Section -->
<section id="contact" class="py-20 px-6 bg-light-grey">
    <div class="max-w-2xl mx-auto opacity-0 fade-in">
        <h2 class="text-4xl font-bold text-center mb-12">Get In Touch</h2>

        <form id="contact-form" class="space-y-6">
            <div>
                <label for="name" class="block text-sm font-semibold mb-2">Name</label>
                <input type="text" id="name" name="name" required
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:border-charcoal">
            </div>

            <div>
                <label for="email" class="block text-sm font-semibold mb-2">Email</label>
                <input type="email" id="email" name="email" required
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:border-charcoal">
            </div>

            <div>
                <label for="message" class="block text-sm font-semibold mb-2">Message</label>
                <textarea id="message" name="message" rows="5" required
                          class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:border-charcoal"></textarea>
            </div>

            <button type="submit"
                    class="w-full bg-charcoal text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition">
                Send Message
            </button>
        </form>

        <div id="form-success" class="hidden mt-6 p-4 bg-green-100 text-green-800 rounded-lg text-center">
            Thank you! Your message has been sent successfully.
        </div>

        <div id="form-error" class="hidden mt-6 p-4 bg-red-100 text-red-800 rounded-lg text-center">
            Oops! Something went wrong. Please try again.
        </div>
    </div>
</section>
{% endblock %}

{% block extra_scripts %}
<script>
// Contact form submission
document.getElementById('contact-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        message: document.getElementById('message').value
    };

    try {
        const response = await fetch('/api/v1/contact', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            document.getElementById('form-success').classList.remove('hidden');
            document.getElementById('form-error').classList.add('hidden');
            document.getElementById('contact-form').reset();
        } else {
            throw new Error('Failed to submit');
        }
    } catch (error) {
        document.getElementById('form-error').classList.remove('hidden');
        document.getElementById('form-success').classList.add('hidden');
    }
});
</script>
{% endblock %}
```

**Step 4: Create project detail template**

Create `backend/app/templates/public/project_detail.html`:

```html
{% extends "base.html" %}

{% block title %}{{ project.title }} - Craig Mackenzie{% endblock %}

{% block content %}
<article class="pt-32 pb-20 px-6">
    <div class="max-w-4xl mx-auto">
        <a href="/#projects" class="text-charcoal hover:underline mb-6 inline-block">← Back to Projects</a>

        <h1 class="text-5xl font-bold mb-4 opacity-0 fade-in">{{ project.title }}</h1>

        {% if project.date %}
        <p class="text-gray-600 mb-8">{{ project.date.strftime('%B %Y') }}</p>
        {% endif %}

        {% if project.media and project.media|length > 0 %}
        <div class="mb-12">
            <img src="{{ project.media[0].url }}" alt="{{ project.media[0].alt_text }}"
                 class="w-full rounded-lg shadow-lg opacity-0 fade-in">
        </div>
        {% endif %}

        {% if project.tech_stack %}
        <div class="flex flex-wrap gap-2 mb-8 opacity-0 fade-in">
            {% for tech in project.tech_stack %}
            <span class="bg-light-grey text-charcoal px-4 py-2 rounded-full">{{ tech }}</span>
            {% endfor %}
        </div>
        {% endif %}

        <div class="prose prose-lg max-w-none opacity-0 fade-in">
            {% if project.case_study %}
            {{ project.case_study|safe }}
            {% else %}
            <p>{{ project.description }}</p>
            {% endif %}
        </div>

        {% if project.project_url %}
        <div class="mt-12 opacity-0 fade-in">
            <a href="{{ project.project_url }}" target="_blank" rel="noopener noreferrer"
               class="inline-block bg-charcoal text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition">
                View Live Project →
            </a>
        </div>
        {% endif %}

        {% if project.media|length > 1 %}
        <div class="mt-12">
            <h2 class="text-2xl font-bold mb-6">Gallery</h2>
            <div class="grid md:grid-cols-2 gap-4">
                {% for media in project.media[1:] %}
                <img src="{{ media.url }}" alt="{{ media.alt_text }}"
                     class="w-full rounded-lg shadow opacity-0 fade-in">
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</article>
{% endblock %}
```

**Step 5: Create CSS file**

Create `backend/static/css/main.css`:

```css
/* Fade-in animation */
.fade-in {
    animation: fadeIn 0.8s ease-in forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Stagger fade-in delays */
.fade-in:nth-child(1) { animation-delay: 0.1s; }
.fade-in:nth-child(2) { animation-delay: 0.2s; }
.fade-in:nth-child(3) { animation-delay: 0.3s; }
.fade-in:nth-child(4) { animation-delay: 0.4s; }
.fade-in:nth-child(5) { animation-delay: 0.5s; }
.fade-in:nth-child(6) { animation-delay: 0.6s; }

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}
```

**Step 6: Create JavaScript file**

Create `backend/static/js/main.js`:

```javascript
// Mobile menu toggle
document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all fade-in elements
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.opacity-0').forEach(el => observer.observe(el));
});
```

**Step 7: Create public router**

Create `backend/app/routers/public.py`:

```python
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.main import templates
from app.services import project_service

router = APIRouter(tags=["public"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """Public home page"""
    projects = project_service.get_projects(db, published_only=True, limit=6)
    return templates.TemplateResponse("public/home.html", {
        "request": request,
        "projects": projects
    })


@router.get("/projects/{slug}", response_class=HTMLResponse)
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    """Public project detail page"""
    project = project_service.get_project_by_slug(db, slug)
    if not project or not project.is_published:
        raise HTTPException(status_code=404, detail="Project not found")

    return templates.TemplateResponse("public/project_detail.html", {
        "request": request,
        "project": project
    })
```

**Step 8: Include public router in main app**

Modify `backend/app/main.py`, add after other routers:

```python
from app.routers import public

app.include_router(public.router)
```

**Step 9: Test public pages**

1. Start server
2. Visit http://127.0.0.1:8000/
3. Create a published project via admin API
4. Refresh home page - project should appear
5. Click on project to view detail page

Expected: Beautiful portfolio pages with dynamic data

**Step 10: Commit**

```bash
git add .
git commit -m "feat: add public portfolio pages with Jinja2 templates"
```

---

## Phase 4: CRM (Leads & Clients)

### Task 7: Contact Form & Lead Management

**Files:**
- Create: `backend/app/schemas/lead.py`
- Create: `backend/app/services/lead_service.py`
- Create: `backend/app/routers/contact.py`
- Create: `backend/app/routers/admin/leads.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/__init__.py`

**Step 1: Create lead schemas**

Create `backend/app/schemas/lead.py`:

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    source: str
    status: LeadStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
```

**Step 2: Create lead service**

Create `backend/app/services/lead_service.py`:

```python
from sqlalchemy.orm import Session
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate
from typing import List, Optional


def create_lead(db: Session, lead_data: LeadCreate, source: str = "Contact Form") -> Lead:
    """Create a new lead"""
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        message=lead_data.message,
        source=source,
        status=LeadStatus.NEW
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """Get lead by ID"""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
) -> List[Lead]:
    """Get list of leads"""
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def update_lead_status(db: Session, lead_id: int, status: LeadStatus) -> Optional[Lead]:
    """Update lead status"""
    lead = get_lead(db, lead_id)
    if not lead:
        return None

    lead.status = status
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a lead"""
    lead = get_lead(db, lead_id)
    if not lead:
        return False

    db.delete(lead)
    db.commit()
    return True
```

**Step 3: Create public contact endpoint**

Create `backend/app/routers/contact.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.lead import ContactFormRequest, LeadResponse
from app.services import lead_service
from app.schemas.lead import LeadCreate

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(
    form_data: ContactFormRequest,
    db: Session = Depends(get_db)
):
    """Public endpoint to submit contact form"""
    lead_data = LeadCreate(
        name=form_data.name,
        email=form_data.email,
        message=form_data.message
    )
    lead = lead_service.create_lead(db, lead_data, source="Contact Form")
    return lead
```

**Step 4: Create leads admin router**

Create `backend/app/routers/admin/leads.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.lead import LeadStatus
from app.schemas.lead import LeadResponse, LeadUpdate
from app.services import lead_service

router = APIRouter(prefix="/admin/leads", tags=["admin-leads"])


@router.get("", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all leads (admin only)"""
    leads = lead_service.get_leads(db, skip=skip, limit=limit, status=status)
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific lead (admin only)"""
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update lead status (admin only)"""
    lead = lead_service.update_lead_status(db, lead_id, lead_data.status)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a lead (admin only)"""
    success = lead_service.delete_lead(db, lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None
```

**Step 5: Update services __init__.py**

Modify `backend/app/services/__init__.py`:

```python
from app.services import project_service, media_service, lead_service

__all__ = ["project_service", "media_service", "lead_service"]
```

**Step 6: Include routers in main app**

Modify `backend/app/main.py`, add after other routers:

```python
from app.routers import contact
from app.routers.admin import leads as admin_leads

app.include_router(contact.router, prefix=settings.API_PREFIX)
app.include_router(admin_leads.router, prefix=settings.API_PREFIX)
```

**Step 7: Test contact form**

1. Start server
2. Visit http://127.0.0.1:8000/ and submit contact form
3. Check that lead is created (use admin API)
4. Test lead filtering by status
5. Update lead status
6. Delete lead

Expected: Contact form creates leads, admin can manage them

**Step 8: Commit**

```bash
git add .
git commit -m "feat: add contact form and lead management"
```

---

### Task 8: Client Management & Lead Conversion

**Files:**
- Create: `backend/app/schemas/client.py`
- Create: `backend/app/services/client_service.py`
- Create: `backend/app/routers/admin/clients.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/__init__.py`
- Modify: `backend/app/services/lead_service.py`

**Step 1: Create client schemas**

Create `backend/app/schemas/client.py`:

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ClientBase(BaseModel):
    company_name: Optional[str] = None
    contact_name: str
    contact_email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    id: int
    company_name: Optional[str]
    contact_name: str
    contact_email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 2: Create client service**

Create `backend/app/services/client_service.py`:

```python
from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from typing import List, Optional


def create_client(db: Session, client_data: ClientCreate, user_id: int) -> Client:
    """Create a new client"""
    client = Client(
        **client_data.model_dump(),
        user_id=user_id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: int, user_id: int) -> Optional[Client]:
    """Get client by ID"""
    return db.query(Client).filter(
        Client.id == client_id,
        Client.user_id == user_id
    ).first()


def get_clients(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get list of clients"""
    return db.query(Client).filter(
        Client.user_id == user_id
    ).order_by(Client.created_at.desc()).offset(skip).limit(limit).all()


def update_client(
    db: Session,
    client_id: int,
    user_id: int,
    client_data: ClientUpdate
) -> Optional[Client]:
    """Update a client"""
    client = get_client(db, client_id, user_id)
    if not client:
        return None

    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int, user_id: int) -> bool:
    """Delete a client"""
    client = get_client(db, client_id, user_id)
    if not client:
        return False

    db.delete(client)
    db.commit()
    return True
```

**Step 3: Add lead conversion to lead service**

Modify `backend/app/services/lead_service.py`, add at the end:

```python
from app.models.client import Client
from app.schemas.client import ClientCreate


def convert_lead_to_client(db: Session, lead_id: int, user_id: int) -> Optional[Client]:
    """Convert a lead to a client"""
    lead = get_lead(db, lead_id)
    if not lead:
        return None

    # Create client from lead
    client_data = ClientCreate(
        contact_name=lead.name,
        contact_email=lead.email,
        notes=f"Converted from lead. Original message: {lead.message}"
    )

    client = Client(
        **client_data.model_dump(),
        user_id=user_id
    )
    db.add(client)

    # Update lead status
    lead.status = LeadStatus.CONVERTED

    db.commit()
    db.refresh(client)
    return client
```

**Step 4: Create clients admin router**

Create `backend/app/routers/admin/clients.py`:

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from app.services import client_service

router = APIRouter(prefix="/admin/clients", tags=["admin-clients"])


@router.get("", response_model=List[ClientListResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all clients (admin only)"""
    clients = client_service.get_clients(db, current_user.id, skip=skip, limit=limit)
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific client (admin only)"""
    client = client_service.get_client(db, client_id, current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new client (admin only)"""
    client = client_service.create_client(db, client_data, current_user.id)
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a client (admin only)"""
    client = client_service.update_client(db, client_id, current_user.id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a client (admin only)"""
    success = client_service.delete_client(db, client_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return None
```

**Step 5: Add lead conversion endpoint**

Modify `backend/app/routers/admin/leads.py`, add at the end:

```python
from app.schemas.client import ClientResponse


@router.post("/{lead_id}/convert", response_model=ClientResponse)
def convert_lead_to_client(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Convert a lead to a client (admin only)"""
    client = lead_service.convert_lead_to_client(db, lead_id, current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="Lead not found")
    return client
```

**Step 6: Update services __init__.py**

Modify `backend/app/services/__init__.py`:

```python
from app.services import project_service, media_service, lead_service, client_service

__all__ = ["project_service", "media_service", "lead_service", "client_service"]
```

**Step 7: Include clients router in main app**

Modify `backend/app/main.py`, add after leads router:

```python
from app.routers.admin import clients as admin_clients

app.include_router(admin_clients.router, prefix=settings.API_PREFIX)
```

**Step 8: Test client management**

1. Start server
2. Create a client via admin API
3. List clients
4. Update client
5. Convert a lead to client
6. Verify lead status changed to "converted"
7. Delete client

Expected: All client operations and lead conversion work correctly

**Step 9: Commit**

```bash
git add .
git commit -m "feat: add client management and lead conversion"
```

---

## Phase 5: Invoicing Integration

### Task 9: Invoice CRUD API

**Files:**
- Create: `backend/app/schemas/invoice.py`
- Create: `backend/app/services/invoice_service.py`
- Create: `backend/app/routers/admin/invoices.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/__init__.py`

**Step 1: Create invoice schemas**

Create `backend/app/schemas/invoice.py`:

```python
from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.invoice import InvoiceStatus


class InvoiceItemBase(BaseModel):
    description: str
    quantity: condecimal(gt=0, max_digits=10, decimal_places=2)
    unit_price: condecimal(ge=0, max_digits=10, decimal_places=2)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    total: Decimal

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    client_id: int
    project_id: Optional[int] = None
    currency: str = "USD"
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    tax_rate: condecimal(ge=0, le=100, max_digits=5, decimal_places=2) = Decimal("0.00")


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    project_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    currency: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    tax_rate: Optional[condecimal(ge=0, le=100, max_digits=5, decimal_places=2)] = None


class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    paid_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: int
    invoice_number: str
    client_id: int
    status: InvoiceStatus
    total: Decimal
    issue_date: datetime
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 2: Create invoice service**

Create `backend/app/services/invoice_service.py`:

```python
from sqlalchemy.orm import Session
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


def generate_invoice_number(db: Session, user_id: int, prefix: str = "INV") -> str:
    """Generate unique invoice number"""
    # Get count of invoices for this user
    count = db.query(Invoice).filter(Invoice.user_id == user_id).count()
    number = count + 1

    # Generate invoice number with year and padded number
    year = datetime.now().year
    invoice_number = f"{prefix}-{year}-{number:04d}"

    # Ensure uniqueness
    while db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first():
        number += 1
        invoice_number = f"{prefix}-{year}-{number:04d}"

    return invoice_number


def calculate_invoice_totals(items: List[InvoiceItemCreate], tax_rate: Decimal) -> dict:
    """Calculate invoice totals"""
    subtotal = sum(item.quantity * item.unit_price for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": total
    }


def create_invoice(db: Session, invoice_data: InvoiceCreate, user_id: int) -> Invoice:
    """Create a new invoice"""
    # Generate invoice number
    invoice_number = generate_invoice_number(db, user_id)

    # Calculate totals
    totals = calculate_invoice_totals(invoice_data.items, invoice_data.tax_rate)

    # Create invoice
    invoice = Invoice(
        user_id=user_id,
        client_id=invoice_data.client_id,
        project_id=invoice_data.project_id,
        invoice_number=invoice_number,
        currency=invoice_data.currency,
        issue_date=invoice_data.issue_date or datetime.utcnow(),
        due_date=invoice_data.due_date,
        notes=invoice_data.notes,
        terms=invoice_data.terms,
        tax_rate=invoice_data.tax_rate,
        subtotal=totals["subtotal"],
        tax_amount=totals["tax_amount"],
        total=totals["total"],
        status=InvoiceStatus.DRAFT
    )
    db.add(invoice)
    db.flush()

    # Create invoice items
    for item_data in invoice_data.items:
        item = InvoiceItem(
            invoice_id=invoice.id,
            **item_data.model_dump()
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, invoice_id: int, user_id: int) -> Optional[Invoice]:
    """Get invoice by ID"""
    return db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()


def get_invoices(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = None,
    client_id: Optional[int] = None
) -> List[Invoice]:
    """Get list of invoices"""
    query = db.query(Invoice).filter(Invoice.user_id == user_id)

    if status:
        query = query.filter(Invoice.status == status)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)

    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


def update_invoice(
    db: Session,
    invoice_id: int,
    user_id: int,
    invoice_data: InvoiceUpdate
) -> Optional[Invoice]:
    """Update an invoice"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return None

    update_data = invoice_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, invoice_id: int, user_id: int) -> bool:
    """Delete an invoice"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return False

    db.delete(invoice)
    db.commit()
    return True


def mark_invoice_paid(db: Session, invoice_id: int, user_id: int) -> Optional[Invoice]:
    """Mark invoice as paid"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return None

    invoice.status = InvoiceStatus.PAID
    invoice.paid_date = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return invoice
```

**Step 3: Create invoices admin router**

Create `backend/app/routers/admin/invoices.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.invoice import InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from app.services import invoice_service

router = APIRouter(prefix="/admin/invoices", tags=["admin-invoices"])


@router.get("", response_model=List[InvoiceListResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all invoices (admin only)"""
    invoices = invoice_service.get_invoices(
        db, current_user.id, skip=skip, limit=limit, status=status, client_id=client_id
    )
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific invoice (admin only)"""
    invoice = invoice_service.get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new invoice (admin only)"""
    invoice = invoice_service.create_invoice(db, invoice_data, current_user.id)
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an invoice (admin only)"""
    invoice = invoice_service.update_invoice(db, invoice_id, current_user.id, invoice_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete an invoice (admin only)"""
    success = invoice_service.delete_invoice(db, invoice_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mark invoice as paid (admin only)"""
    invoice = invoice_service.mark_invoice_paid(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
```

**Step 4: Update services __init__.py**

Modify `backend/app/services/__init__.py`:

```python
from app.services import project_service, media_service, lead_service, client_service, invoice_service

__all__ = ["project_service", "media_service", "lead_service", "client_service", "invoice_service"]
```

**Step 5: Include invoices router in main app**

Modify `backend/app/main.py`, add after clients router:

```python
from app.routers.admin import invoices as admin_invoices

app.include_router(admin_invoices.router, prefix=settings.API_PREFIX)
```

**Step 6: Test invoice management**

1. Start server
2. Create a client first (invoices need a client)
3. Create an invoice with line items
4. List invoices
5. Filter by status and client
6. Update invoice
7. Mark invoice as paid
8. Delete invoice

Expected: All invoice operations work correctly with automatic calculations

**Step 9: Commit**

```bash
git add .
git commit -m "feat: add invoice CRUD API with automatic calculations"
```

---

## Phase 6: Admin Panel Frontend

### Task 10: Admin Dashboard & Navigation

**Files:**
- Create: `backend/app/templates/admin/base.html`
- Create: `backend/app/templates/admin/login.html`
- Create: `backend/app/templates/admin/dashboard.html`
- Create: `backend/app/templates/components/admin_nav.html`
- Create: `backend/static/js/admin.js`
- Create: `backend/static/js/auth.js`
- Create: `backend/app/routers/admin/pages.py`
- Modify: `backend/app/main.py`

**Step 1: Create admin base template**

Create `backend/app/templates/admin/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin Panel{% endblock %} - Mackenzie-Dev</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        charcoal: '#2d3748',
                        'light-grey': '#f7fafc',
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="/static/css/main.css">
    {% block extra_head %}{% endblock %}
</head>
<body class="bg-light-grey">
    {% if show_nav|default(true) %}
    {% include 'components/admin_nav.html' %}
    {% endif %}

    <main class="{% if show_nav|default(true) %}ml-0 md:ml-64{% endif %} p-6 min-h-screen">
        {% block content %}{% endblock %}
    </main>

    <script src="/static/js/auth.js"></script>
    <script src="/static/js/admin.js"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Step 2: Create admin navigation**

Create `backend/app/templates/components/admin_nav.html`:

```html
<nav class="fixed left-0 top-0 h-full w-64 bg-charcoal text-white p-6 hidden md:block">
    <div class="mb-8">
        <h1 class="text-2xl font-bold">Mackenzie-Dev</h1>
        <p class="text-gray-400 text-sm">Admin Panel</p>
    </div>

    <ul class="space-y-2">
        <li>
            <a href="/admin" class="block px-4 py-2 rounded hover:bg-gray-700 transition">
                Dashboard
            </a>
        </li>
        <li>
            <a href="/admin/projects" class="block px-4 py-2 rounded hover:bg-gray-700 transition">
                Projects
            </a>
        </li>
        <li>
            <a href="/admin/leads" class="block px-4 py-2 rounded hover:bg-gray-700 transition">
                Leads
            </a>
        </li>
        <li>
            <a href="/admin/clients" class="block px-4 py-2 rounded hover:bg-gray-700 transition">
                Clients
            </a>
        </li>
        <li>
            <a href="/admin/invoices" class="block px-4 py-2 rounded hover:bg-gray-700 transition">
                Invoices
            </a>
        </li>
    </ul>

    <div class="mt-auto pt-8">
        <button onclick="logout()" class="w-full px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition">
            Logout
        </button>
    </div>
</nav>

<div class="md:hidden fixed top-0 left-0 right-0 bg-charcoal text-white p-4 z-50">
    <div class="flex justify-between items-center">
        <h1 class="text-xl font-bold">Mackenzie-Dev</h1>
        <button id="mobile-admin-menu-btn">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
        </button>
    </div>
</div>
```

**Step 3: Create login page**

Create `backend/app/templates/admin/login.html`:

```html
{% extends "admin/base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-3xl font-bold mb-6 text-center">Admin Login</h2>

        <form id="login-form" class="space-y-4">
            <div>
                <label for="email" class="block text-sm font-semibold mb-2">Email</label>
                <input type="email" id="email" name="email" required
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:border-charcoal">
            </div>

            <div>
                <label for="password" class="block text-sm font-semibold mb-2">Password</label>
                <input type="password" id="password" name="password" required
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:border-charcoal">
            </div>

            <div id="login-error" class="hidden p-3 bg-red-100 text-red-800 rounded-lg text-sm">
                Invalid email or password
            </div>

            <button type="submit"
                    class="w-full bg-charcoal text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition">
                Login
            </button>
        </form>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch('/api/v1/auth/token', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/admin';
        } else {
            document.getElementById('login-error').classList.remove('hidden');
        }
    } catch (error) {
        document.getElementById('login-error').classList.remove('hidden');
    }
});
</script>
{% endblock %}
```

**Step 4: Create dashboard page**

Create `backend/app/templates/admin/dashboard.html`:

```html
{% extends "admin/base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="md:mt-0 mt-16">
    <h1 class="text-4xl font-bold mb-8">Dashboard</h1>

    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-gray-600 text-sm font-semibold mb-2">Total Projects</h3>
            <p class="text-3xl font-bold" id="total-projects">-</p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-gray-600 text-sm font-semibold mb-2">New Leads</h3>
            <p class="text-3xl font-bold" id="new-leads">-</p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-gray-600 text-sm font-semibold mb-2">Total Clients</h3>
            <p class="text-3xl font-bold" id="total-clients">-</p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-gray-600 text-sm font-semibold mb-2">Pending Invoices</h3>
            <p class="text-3xl font-bold" id="pending-invoices">-</p>
        </div>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold mb-4">Recent Leads</h2>
            <div id="recent-leads">Loading...</div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold mb-4">Recent Invoices</h2>
            <div id="recent-invoices">Loading...</div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadDashboard() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/admin/login';
        return;
    }

    const headers = {
        'Authorization': `Bearer ${token}`
    };

    try {
        // Load projects count
        const projectsRes = await fetch('/api/v1/admin/projects', { headers });
        const projects = await projectsRes.json();
        document.getElementById('total-projects').textContent = projects.length;

        // Load leads count
        const leadsRes = await fetch('/api/v1/admin/leads?status=new', { headers });
        const leads = await leadsRes.json();
        document.getElementById('new-leads').textContent = leads.length;

        // Load clients count
        const clientsRes = await fetch('/api/v1/admin/clients', { headers });
        const clients = await clientsRes.json();
        document.getElementById('total-clients').textContent = clients.length;

        // Load invoices count
        const invoicesRes = await fetch('/api/v1/admin/invoices?status=sent', { headers });
        const invoices = await invoicesRes.json();
        document.getElementById('pending-invoices').textContent = invoices.length;

        // Display recent leads
        const recentLeadsRes = await fetch('/api/v1/admin/leads?limit=5', { headers });
        const recentLeads = await recentLeadsRes.json();
        const leadsHtml = recentLeads.map(lead => `
            <div class="border-b py-3">
                <p class="font-semibold">${lead.name}</p>
                <p class="text-sm text-gray-600">${lead.email}</p>
            </div>
        `).join('');
        document.getElementById('recent-leads').innerHTML = leadsHtml || '<p class="text-gray-500">No leads yet</p>';

        // Display recent invoices
        const recentInvoicesRes = await fetch('/api/v1/admin/invoices?limit=5', { headers });
        const recentInvoices = await recentInvoicesRes.json();
        const invoicesHtml = recentInvoices.map(inv => `
            <div class="border-b py-3 flex justify-between">
                <div>
                    <p class="font-semibold">${inv.invoice_number}</p>
                    <p class="text-sm text-gray-600">${inv.status}</p>
                </div>
                <p class="font-bold">$${inv.total}</p>
            </div>
        `).join('');
        document.getElementById('recent-invoices').innerHTML = invoicesHtml || '<p class="text-gray-500">No invoices yet</p>';

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

loadDashboard();
</script>
{% endblock %}
```

**Step 5: Create auth utilities**

Create `backend/static/js/auth.js`:

```javascript
function getToken() {
    return localStorage.getItem('access_token');
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/admin/login';
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/admin/login';
    }
}

async function fetchWithAuth(url, options = {}) {
    const token = getToken();

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    return response;
}
```

**Step 6: Create admin utilities**

Create `backend/static/js/admin.js`:

```javascript
// Mobile menu toggle
document.getElementById('mobile-admin-menu-btn')?.addEventListener('click', () => {
    alert('Mobile menu - to be implemented');
});

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
```

**Step 7: Create admin pages router**

Create `backend/app/routers/admin/pages.py`:

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.main import templates

router = APIRouter(prefix="/admin", tags=["admin-pages"])


@router.get("/login", response_class=HTMLResponse)
def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "show_nav": False
    })


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request
    })
```

**Step 8: Include admin pages router**

Modify `backend/app/main.py`, add after other routers:

```python
from app.routers.admin import pages as admin_pages

app.include_router(admin_pages.router)
```

**Step 9: Test admin panel**

1. Start server
2. Visit http://127.0.0.1:8000/admin - should redirect to login
3. Login with your admin credentials
4. View dashboard with statistics
5. Test logout

Expected: Admin panel with working authentication and dashboard

**Step 10: Commit**

```bash
git add .
git commit -m "feat: add admin panel dashboard and authentication"
```

---

## Deployment & Final Steps

### Task 11: Environment Configuration & README

**Files:**
- Create: `backend/README.md`
- Create: `backend/.env.production.example`
- Modify: `backend/requirements.txt`

**Step 1: Add production dependencies**

Modify `backend/requirements.txt`, add:

```
gunicorn==21.2.0
python-dotenv==1.0.0
```

**Step 2: Create production env example**

Create `backend/.env.production.example`:

```
# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Security
SECRET_KEY=your-very-secure-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
```

**Step 3: Create comprehensive README**

Create `backend/README.md`:

```markdown
# Mackenzie-Dev - Portfolio & Business Management System

A full-stack web application combining a dynamic portfolio, CRM, and invoicing system.

## Features

- **Portfolio CMS**: Manage and showcase projects with images
- **Contact Form**: Capture leads from website visitors
- **CRM**: Manage leads and clients
- **Invoicing**: Create and track invoices linked to clients and projects
- **Admin Panel**: Secure admin interface for business management
- **Public Portfolio**: Beautiful, responsive portfolio website

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Frontend**: Jinja2, TailwindCSS, Vanilla JavaScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **Auth**: JWT with role-based access control

## Local Development Setup

### Prerequisites

- Python 3.9+
- pip
- virtualenv

### Installation

1. Clone the repository:
```bash
cd cm.dev/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and set SECRET_KEY:
```
SECRET_KEY=your-random-secret-key-here
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Create admin user:
```bash
python create_admin.py "your@email.com" "password" "Your Name" "Your Company"
```

8. Start development server:
```bash
uvicorn app.main:app --reload
```

9. Visit:
- Public site: http://127.0.0.1:8000
- Admin panel: http://127.0.0.1:8000/admin
- API docs: http://127.0.0.1:8000/api/docs

## Project Structure

```
backend/
├── app/
│   ├── core/           # Config, security, dependencies
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API routes
│   │   ├── admin/      # Admin-only routes
│   │   ├── auth.py
│   │   ├── contact.py
│   │   └── public.py
│   ├── services/       # Business logic
│   ├── templates/      # Jinja2 templates
│   │   ├── admin/
│   │   ├── public/
│   │   └── components/
│   ├── db.py
│   └── main.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── alembic/            # Database migrations
├── requirements.txt
└── .env
```

## API Endpoints

### Public
- `GET /` - Home page
- `GET /projects/{slug}` - Project detail
- `POST /api/v1/contact` - Submit contact form

### Authentication
- `POST /api/v1/auth/token` - Login

### Admin (Protected)
- `GET /api/v1/admin/projects` - List projects
- `POST /api/v1/admin/projects` - Create project
- `POST /api/v1/admin/projects/{id}/media` - Upload media
- `GET /api/v1/admin/leads` - List leads
- `POST /api/v1/admin/leads/{id}/convert` - Convert lead to client
- `GET /api/v1/admin/clients` - List clients
- `GET /api/v1/admin/invoices` - List invoices
- `POST /api/v1/admin/invoices/{id}/mark-paid` - Mark invoice as paid

## Deployment

### PythonAnywhere

1. Upload code to PythonAnywhere

2. Create PostgreSQL database

3. Set environment variables in Web tab

4. Configure WSGI file:
```python
import sys
path = '/home/yourusername/cm.dev/backend'
if path not in sys.path:
    sys.path.append(path)

from app.main import app as application
```

5. Run migrations:
```bash
cd ~/cm.dev/backend
alembic upgrade head
```

6. Create admin user

7. Reload web app

## Testing

Run tests:
```bash
pytest
```

## License

Proprietary - Craig Mackenzie

## Support

For issues or questions, contact: craig@mackenzie.dev
```

**Step 4: Commit**

```bash
git add .
git commit -m "docs: add comprehensive README and deployment configuration"
```

---

## Summary

This implementation plan provides a complete, production-ready MVP with:

✅ **95-125 hours of work broken into bite-sized tasks**
✅ **All models, schemas, services, and routers**
✅ **Public portfolio with dynamic data**
✅ **Full CRM (leads + clients)**
✅ **Complete invoicing system**
✅ **Admin panel with authentication**
✅ **Deployment-ready configuration**

Each task includes:
- Exact file paths
- Complete code (not pseudocode)
- Testing steps with expected outputs
- Commit messages following conventions

## Next Steps After Plan

1. **Execute the plan** using superpowers:executing-plans or superpowers:subagent-driven-development
2. **Test thoroughly** after each phase
3. **Deploy to PythonAnywhere**
4. **Add content** (portfolio projects, company info)
5. **Go live!**

Future enhancements (v1.1+):
- Client portal (read-only access for clients)
- PDF invoice generation
- Email notifications
- Advanced reporting
- Tags/categories for projects
- Multi-file upload interface

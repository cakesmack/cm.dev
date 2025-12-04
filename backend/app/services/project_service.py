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
    """Get list of projects - sorted by date (or created_at if no date)"""
    from sqlalchemy import func
    query = db.query(Project)
    if published_only:
        query = query.filter(Project.is_published == True)
    # Sort by date if available, otherwise use created_at
    # COALESCE returns the first non-NULL value
    return query.order_by(
        func.coalesce(Project.date, func.date(Project.created_at)).desc()
    ).offset(skip).limit(limit).all()


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

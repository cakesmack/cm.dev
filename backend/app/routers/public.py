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

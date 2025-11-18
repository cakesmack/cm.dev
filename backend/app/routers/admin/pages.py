from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.services import client_service

templates = Jinja2Templates(directory="app/templates")
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


@router.get("/projects", response_class=HTMLResponse)
def admin_projects_page(request: Request):
    """Admin projects management page"""
    return templates.TemplateResponse("admin/projects.html", {
        "request": request
    })


@router.get("/leads", response_class=HTMLResponse)
def admin_leads_page(request: Request):
    """Admin leads management page"""
    return templates.TemplateResponse("admin/leads.html", {
        "request": request
    })


@router.get("/clients", response_class=HTMLResponse)
def admin_clients_page(request: Request):
    """Admin clients management page"""
    return templates.TemplateResponse("admin/clients.html", {
        "request": request
    })


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def admin_client_detail_page(request: Request, client_id: int):
    """Admin client detail page"""
    return templates.TemplateResponse("admin/client_detail.html", {
        "request": request,
        "client_id": client_id
    })


@router.get("/invoices", response_class=HTMLResponse)
def admin_invoices_page(request: Request):
    """Admin invoices management page"""
    return templates.TemplateResponse("admin/invoices.html", {
        "request": request
    })


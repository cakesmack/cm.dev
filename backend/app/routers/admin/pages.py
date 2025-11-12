from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


@router.get("/invoices", response_class=HTMLResponse)
def admin_invoices_page(request: Request):
    """Admin invoices management page"""
    return templates.TemplateResponse("admin/invoices.html", {
        "request": request
    })

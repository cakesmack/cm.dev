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

from app.routers import auth, public, contact
from app.routers.admin import projects as admin_projects
from app.routers.admin import media as admin_media
from app.routers.admin import leads as admin_leads

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(admin_projects.router, prefix=settings.API_PREFIX)
app.include_router(admin_media.router, prefix=settings.API_PREFIX)
app.include_router(contact.router, prefix=settings.API_PREFIX)
app.include_router(admin_leads.router, prefix=settings.API_PREFIX)
app.include_router(public.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}

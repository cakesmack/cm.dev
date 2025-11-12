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

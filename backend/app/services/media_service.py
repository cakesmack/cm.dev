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


async def validate_image(file: UploadFile) -> bool:
    """Validate image file"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    # Check file size
    contents = await file.read()
    file_size = len(contents)
    await file.seek(0)  # Reset file pointer for later reading

    if file_size > MAX_FILE_SIZE:
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

    # Additional file size check
    if len(contents) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")

    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except IOError as e:
        # Clean up partially written file if it exists
        if file_path.exists():
            file_path.unlink()
        raise IOError(f"Failed to save file: {str(e)}")

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

    # Delete file from disk - use safe path construction
    filename = Path(media.url).name
    file_path = UPLOAD_DIR / filename
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

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMedia
from app.schemas.project import ProjectMediaCreate

UPLOAD_DIR = Path("static/uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB


async def validate_media(file: UploadFile) -> tuple[bool, str]:
    """Validate media file - returns (is_valid, media_type)"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, ""

    # Determine media type
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        media_type = "image"
        max_size = MAX_IMAGE_SIZE
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        media_type = "video"
        max_size = MAX_VIDEO_SIZE
    else:
        return False, ""

    # Check file size
    contents = await file.read()
    file_size = len(contents)
    await file.seek(0)  # Reset file pointer for later reading

    if file_size > max_size:
        return False, ""

    return True, media_type


async def validate_image(file: UploadFile) -> bool:
    """Validate image file (legacy - kept for backwards compatibility)"""
    is_valid, media_type = await validate_media(file)
    return is_valid and media_type == "image"


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

    # Determine max size based on file type
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        max_size = MAX_IMAGE_SIZE
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        max_size = MAX_VIDEO_SIZE
    else:
        raise ValueError("Invalid file type")

    # Additional file size check
    if len(contents) > max_size:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size / (1024 * 1024):.0f}MB")

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


def get_media_by_type_and_order(db: Session, project_id: int, media_type: str, display_order: int) -> Optional[ProjectMedia]:
    """Get media by project, type, and display order"""
    return db.query(ProjectMedia).filter(
        ProjectMedia.project_id == project_id,
        ProjectMedia.media_type == media_type,
        ProjectMedia.display_order == display_order
    ).first()


def replace_or_create_media(
    db: Session,
    project_id: int,
    url: str,
    media_type: str = "image",
    display_order: int = 0,
    alt_text: Optional[str] = None
) -> Optional[ProjectMedia]:
    """Replace existing media at display_order or create new one"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    # Check if media already exists at this position
    existing_media = get_media_by_type_and_order(db, project_id, media_type, display_order)

    if existing_media:
        # Delete old file
        old_filename = Path(existing_media.url).name
        old_file_path = UPLOAD_DIR / old_filename
        if old_file_path.exists():
            old_file_path.unlink()

        # Update existing record
        existing_media.url = url
        existing_media.alt_text = alt_text or ""
        db.commit()
        db.refresh(existing_media)
        return existing_media
    else:
        # Create new media record
        media = ProjectMedia(
            project_id=project_id,
            media_type=media_type,
            url=url,
            alt_text=alt_text or "",
            display_order=display_order
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        return media

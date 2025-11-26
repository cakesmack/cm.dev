import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from app.models.project import Project, ProjectMedia
from app.schemas.project import ProjectMediaCreate

# Configure Cloudinary from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

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
    """Save uploaded file to Cloudinary and return URL"""
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    public_id = f"portfolio/{uuid.uuid4()}"

    # Save file
    contents = await file.read()

    # Determine max size and resource type based on file type
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        max_size = MAX_IMAGE_SIZE
        resource_type = "image"
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        max_size = MAX_VIDEO_SIZE
        resource_type = "video"
    else:
        raise ValueError("Invalid file type")

    # File size check
    if len(contents) > max_size:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size / (1024 * 1024):.0f}MB")

    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            contents,
            public_id=public_id,
            resource_type=resource_type,
            folder="portfolio"
        )

        # Return the secure URL from Cloudinary
        return upload_result["secure_url"]
    except Exception as e:
        raise IOError(f"Failed to upload file to Cloudinary: {str(e)}")


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
    """Delete project media from Cloudinary and database"""
    media = db.query(ProjectMedia).filter(ProjectMedia.id == media_id).first()
    if not media:
        return False

    # Delete file from Cloudinary
    try:
        # Extract public_id from Cloudinary URL
        # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/public_id.ext
        if "cloudinary.com" in media.url:
            url_parts = media.url.split("/")
            # Find the version number (starts with 'v')
            version_index = next((i for i, part in enumerate(url_parts) if part.startswith('v') and part[1:].isdigit()), None)
            if version_index:
                # Everything after version is the public_id (including folder)
                public_id_with_ext = "/".join(url_parts[version_index + 1:])
                # Remove file extension
                public_id = public_id_with_ext.rsplit(".", 1)[0]

                # Determine resource type
                resource_type = "video" if media.media_type == "video" else "image"

                # Delete from Cloudinary
                cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete from Cloudinary: {str(e)}")

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
        # Delete old file from Cloudinary
        try:
            if "cloudinary.com" in existing_media.url:
                url_parts = existing_media.url.split("/")
                version_index = next((i for i, part in enumerate(url_parts) if part.startswith('v') and part[1:].isdigit()), None)
                if version_index:
                    public_id_with_ext = "/".join(url_parts[version_index + 1:])
                    public_id = public_id_with_ext.rsplit(".", 1)[0]
                    resource_type = "video" if existing_media.media_type == "video" else "image"
                    cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        except Exception as e:
            print(f"Warning: Failed to delete old file from Cloudinary: {str(e)}")

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

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
    client_id: Optional[int] = None
    title: str
    short_description: Optional[str] = None
    description: str
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[date] = None
    is_published: bool = False
    is_featured: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    client_id: Optional[int] = None
    title: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[date] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None


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
    short_description: Optional[str] = None
    description: str
    is_published: bool
    is_featured: bool
    date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

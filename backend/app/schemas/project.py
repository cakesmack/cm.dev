from pydantic import BaseModel, validator
from datetime import date as DateType, datetime as DateTimeType
from typing import Optional, List, Dict
import re


class ProjectMetricBase(BaseModel):
    icon_type: str
    icon_value: str
    metric_value: str
    metric_label: str
    display_order: int = 0


class ProjectMetricResponse(ProjectMetricBase):
    id: int
    project_id: int
    created_at: DateTimeType
    updated_at: DateTimeType

    class Config:
        from_attributes = True


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
    created_at: DateTimeType

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    client_id: Optional[int] = None
    title: str
    short_description: Optional[str] = None
    description: str
    badge_label: Optional[str] = None
    purpose: Optional[str] = None
    summary: Optional[str] = None
    key_features: Optional[List[Dict[str, str]]] = None
    outcome: Optional[str] = None
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[DateType] = None
    is_published: bool = False
    is_featured: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    client_id: Optional[int] = None
    title: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    badge_label: Optional[str] = None
    purpose: Optional[str] = None
    summary: Optional[str] = None
    key_features: Optional[List[Dict[str, str]]] = None
    outcome: Optional[str] = None
    case_study: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    date: Optional[DateType] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    slug: str
    created_at: DateTimeType
    updated_at: DateTimeType
    media: List[ProjectMediaResponse] = []
    metrics: List[ProjectMetricResponse] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    description: str
    badge_label: Optional[str] = None
    purpose: Optional[str] = None
    summary: Optional[str] = None
    key_features: Optional[List[Dict[str, str]]] = None
    outcome: Optional[str] = None
    is_published: bool
    is_featured: bool
    date: Optional[DateType] = None
    created_at: DateTimeType

    class Config:
        from_attributes = True

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectMetricBase(BaseModel):
    icon_type: str  # 'emoji' or 'lucide'
    icon_value: str  # emoji character or lucide icon name
    metric_value: str  # e.g., "6-8 hours", "100%"
    metric_label: str  # e.g., "saved weekly", "paper elimination"
    display_order: int = 0


class ProjectMetricCreate(ProjectMetricBase):
    pass


class ProjectMetricUpdate(BaseModel):
    icon_type: Optional[str] = None
    icon_value: Optional[str] = None
    metric_value: Optional[str] = None
    metric_label: Optional[str] = None
    display_order: Optional[int] = None


class ProjectMetricResponse(ProjectMetricBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

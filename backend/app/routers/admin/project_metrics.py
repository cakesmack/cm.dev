from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.project_metric import ProjectMetric
from app.schemas.project_metric import ProjectMetricCreate, ProjectMetricResponse, ProjectMetricUpdate

router = APIRouter(prefix="/admin/projects", tags=["admin-project-metrics"])


@router.post("/{project_id}/metrics", response_model=ProjectMetricResponse, status_code=status.HTTP_201_CREATED)
def create_project_metric(
    project_id: int,
    metric_data: ProjectMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new metric for a project (admin only)"""
    metric = ProjectMetric(
        project_id=project_id,
        **metric_data.model_dump()
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@router.get("/{project_id}/metrics", response_model=List[ProjectMetricResponse])
def list_project_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all metrics for a project (admin only)"""
    metrics = db.query(ProjectMetric).filter(
        ProjectMetric.project_id == project_id
    ).order_by(ProjectMetric.display_order).all()
    return metrics


@router.put("/metrics/{metric_id}", response_model=ProjectMetricResponse)
def update_project_metric(
    metric_id: int,
    metric_data: ProjectMetricUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a project metric (admin only)"""
    metric = db.query(ProjectMetric).filter(ProjectMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    update_data = metric_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(metric, field, value)

    db.commit()
    db.refresh(metric)
    return metric


@router.delete("/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a project metric (admin only)"""
    metric = db.query(ProjectMetric).filter(ProjectMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    db.delete(metric)
    db.commit()
    return None

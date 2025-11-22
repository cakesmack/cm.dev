from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class ProjectMetric(Base):
    """Metrics/achievements for projects (e.g., '6-8 hours saved weekly')"""
    __tablename__ = "project_metrics"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Icon configuration
    icon_type = Column(String, nullable=False)  # 'emoji' or 'lucide'
    icon_value = Column(String, nullable=False)  # emoji character or lucide icon name

    # Metric data
    metric_value = Column(String, nullable=False)  # e.g., "6-8 hours", "100%", "30+"
    metric_label = Column(String, nullable=False)  # e.g., "saved weekly", "paper elimination"

    # Ordering
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="metrics")

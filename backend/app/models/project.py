from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Project(Base):
    """Portfolio project"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    short_description = Column(String(200), nullable=True)  # Brief preview for cards
    description = Column(Text, nullable=False)  # Full description
    case_study = Column(Text, nullable=True)  # Long markdown content
    tech_stack = Column(JSON, nullable=True)  # List of technologies
    project_url = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="projects")
    media = relationship("ProjectMedia", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("ProjectMetric", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project")


class ProjectMedia(Base):
    """Media files for projects"""
    __tablename__ = "project_media"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    media_type = Column(String, default="image", nullable=False)  # image, video
    url = Column(String, nullable=False)
    alt_text = Column(String, nullable=True)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="media")

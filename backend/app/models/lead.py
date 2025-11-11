from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from datetime import datetime
import enum
from app.db import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class Lead(Base):
    """Lead from contact form submissions"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String, default="Contact Form", nullable=False)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

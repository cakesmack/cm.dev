from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class User(Base):
    """Admin user (business owner - you)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    role = Column(String, default="admin", nullable=False)  # Only 'admin' for MVP
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")

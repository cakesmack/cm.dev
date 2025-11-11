from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Client(Base):
    """Client/customer of the business"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String, nullable=True)
    contact_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    tax_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")

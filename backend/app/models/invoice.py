from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from decimal import Decimal
import enum
from app.db import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    """Invoice"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    invoice_number = Column(String, nullable=False, unique=True, index=True)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    currency = Column(String, default="USD", nullable=False)

    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)

    subtotal = Column(Numeric(10, 2), default=Decimal("0.00"))
    tax_rate = Column(Numeric(5, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(10, 2), default=Decimal("0.00"))
    total = Column(Numeric(10, 2), default=Decimal("0.00"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    """Invoice line item"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

    @hybrid_property
    def total(self):
        return self.quantity * self.unit_price

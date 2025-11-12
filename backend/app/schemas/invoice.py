from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.invoice import InvoiceStatus


class InvoiceItemBase(BaseModel):
    description: str
    quantity: condecimal(gt=0, max_digits=10, decimal_places=2)
    unit_price: condecimal(ge=0, max_digits=10, decimal_places=2)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    total: Decimal

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    client_id: int
    project_id: Optional[int] = None
    currency: str = "USD"
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    tax_rate: condecimal(ge=0, le=100, max_digits=5, decimal_places=2) = Decimal("0.00")


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    project_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    currency: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    tax_rate: Optional[condecimal(ge=0, le=100, max_digits=5, decimal_places=2)] = None


class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    paid_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: int
    invoice_number: str
    client_id: int
    status: InvoiceStatus
    total: Decimal
    issue_date: datetime
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.invoice import InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from app.services import invoice_service

router = APIRouter(prefix="/admin/invoices", tags=["admin-invoices"])


@router.get("", response_model=List[InvoiceListResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all invoices (admin only)"""
    invoices = invoice_service.get_invoices(
        db, current_user.id, skip=skip, limit=limit, status=status, client_id=client_id
    )
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific invoice (admin only)"""
    invoice = invoice_service.get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new invoice (admin only)"""
    invoice = invoice_service.create_invoice(db, invoice_data, current_user.id)
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an invoice (admin only)"""
    invoice = invoice_service.update_invoice(db, invoice_id, current_user.id, invoice_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete an invoice (admin only)"""
    success = invoice_service.delete_invoice(db, invoice_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mark invoice as paid (admin only)"""
    invoice = invoice_service.mark_invoice_paid(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

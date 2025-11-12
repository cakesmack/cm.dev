from sqlalchemy.orm import Session
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


def generate_invoice_number(db: Session, user_id: int, prefix: str = "INV") -> str:
    """Generate unique invoice number"""
    # Get count of invoices for this user
    count = db.query(Invoice).filter(Invoice.user_id == user_id).count()
    number = count + 1

    # Generate invoice number with year and padded number
    year = datetime.now().year
    invoice_number = f"{prefix}-{year}-{number:04d}"

    # Ensure uniqueness
    while db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first():
        number += 1
        invoice_number = f"{prefix}-{year}-{number:04d}"

    return invoice_number


def calculate_invoice_totals(items: List[InvoiceItemCreate], tax_rate: Decimal) -> dict:
    """Calculate invoice totals"""
    subtotal = sum(item.quantity * item.unit_price for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": total
    }


def create_invoice(db: Session, invoice_data: InvoiceCreate, user_id: int) -> Invoice:
    """Create a new invoice"""
    # Generate invoice number
    invoice_number = generate_invoice_number(db, user_id)

    # Calculate totals
    totals = calculate_invoice_totals(invoice_data.items, invoice_data.tax_rate)

    # Create invoice
    invoice = Invoice(
        user_id=user_id,
        client_id=invoice_data.client_id,
        project_id=invoice_data.project_id,
        invoice_number=invoice_number,
        currency=invoice_data.currency,
        issue_date=invoice_data.issue_date or datetime.utcnow(),
        due_date=invoice_data.due_date,
        notes=invoice_data.notes,
        terms=invoice_data.terms,
        tax_rate=invoice_data.tax_rate,
        subtotal=totals["subtotal"],
        tax_amount=totals["tax_amount"],
        total=totals["total"],
        status=InvoiceStatus.DRAFT
    )
    db.add(invoice)
    db.flush()

    # Create invoice items
    for item_data in invoice_data.items:
        item = InvoiceItem(
            invoice_id=invoice.id,
            **item_data.model_dump()
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, invoice_id: int, user_id: int) -> Optional[Invoice]:
    """Get invoice by ID"""
    return db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()


def get_invoices(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = None,
    client_id: Optional[int] = None
) -> List[Invoice]:
    """Get list of invoices"""
    query = db.query(Invoice).filter(Invoice.user_id == user_id)

    if status:
        query = query.filter(Invoice.status == status)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)

    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


def update_invoice(
    db: Session,
    invoice_id: int,
    user_id: int,
    invoice_data: InvoiceUpdate
) -> Optional[Invoice]:
    """Update an invoice"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return None

    update_data = invoice_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, invoice_id: int, user_id: int) -> bool:
    """Delete an invoice"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return False

    db.delete(invoice)
    db.commit()
    return True


def mark_invoice_paid(db: Session, invoice_id: int, user_id: int) -> Optional[Invoice]:
    """Mark invoice as paid"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return None

    invoice.status = InvoiceStatus.PAID
    invoice.paid_date = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return invoice

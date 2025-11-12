from sqlalchemy.orm import Session
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate
from typing import List, Optional


def create_lead(db: Session, lead_data: LeadCreate, source: str = "Contact Form") -> Lead:
    """Create a new lead"""
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        message=lead_data.message,
        source=source,
        status=LeadStatus.NEW
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """Get lead by ID"""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
) -> List[Lead]:
    """Get list of leads"""
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def update_lead_status(db: Session, lead_id: int, status: LeadStatus) -> Optional[Lead]:
    """Update lead status"""
    lead = get_lead(db, lead_id)
    if not lead:
        return None

    lead.status = status
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a lead"""
    lead = get_lead(db, lead_id)
    if not lead:
        return False

    db.delete(lead)
    db.commit()
    return True


from app.models.client import Client
from app.schemas.client import ClientCreate


def convert_lead_to_client(db: Session, lead_id: int, user_id: int) -> Optional[Client]:
    """Convert a lead to a client"""
    lead = get_lead(db, lead_id)
    if not lead:
        return None

    # Create client from lead
    client_data = ClientCreate(
        contact_name=lead.name,
        contact_email=lead.email,
        notes=f"Converted from lead. Original message: {lead.message}"
    )

    client = Client(
        **client_data.model_dump(),
        user_id=user_id
    )
    db.add(client)

    # Update lead status
    lead.status = LeadStatus.CONVERTED

    db.commit()
    db.refresh(client)
    return client

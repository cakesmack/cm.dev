from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.lead import ContactFormRequest, LeadResponse
from app.services import lead_service
from app.services import email_service
from app.schemas.lead import LeadCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(
    form_data: ContactFormRequest,
    db: Session = Depends(get_db)
):
    """Public endpoint to submit contact form"""
    # Save lead to database
    lead_data = LeadCreate(
        name=form_data.name,
        email=form_data.email,
        message=form_data.message
    )
    lead = lead_service.create_lead(db, lead_data, source="Contact Form")

    # Send email notification (non-blocking - don't fail if email fails)
    try:
        email_service.send_contact_form_notification(
            name=form_data.name,
            email=form_data.email,
            message=form_data.message
        )
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        # Continue anyway - the lead is saved in the database

    return lead

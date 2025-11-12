from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.lead import LeadStatus
from app.schemas.lead import LeadResponse, LeadUpdate
from app.services import lead_service

router = APIRouter(prefix="/admin/leads", tags=["admin-leads"])


@router.get("", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all leads (admin only)"""
    leads = lead_service.get_leads(db, skip=skip, limit=limit, status=status)
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific lead (admin only)"""
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update lead status (admin only)"""
    lead = lead_service.update_lead_status(db, lead_id, lead_data.status)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a lead (admin only)"""
    success = lead_service.delete_lead(db, lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None


from app.schemas.client import ClientResponse, ClientCreate


@router.post("/{lead_id}/convert", response_model=ClientResponse)
def convert_lead_to_client(
    lead_id: int,
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Convert a lead to a client with full client details (admin only)"""
    client = lead_service.convert_lead_to_client(db, lead_id, current_user.id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Lead not found")
    return client

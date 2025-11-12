from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    source: str
    status: LeadStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

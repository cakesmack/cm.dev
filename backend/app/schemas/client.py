from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.project import ProjectListResponse


class ClientBase(BaseModel):
    company_name: Optional[str] = None
    contact_name: str
    contact_email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    projects: List['ProjectListResponse'] = []

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    id: int
    company_name: Optional[str]
    contact_name: str
    contact_email: str
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Resolve forward references
from app.schemas.project import ProjectListResponse
ClientResponse.model_rebuild()

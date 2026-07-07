from app.schemas.contact import ContactSummary
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LeadBase(BaseModel):
    clinic_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "New"
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    clinic_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    contacts: list[ContactSummary] = []

    model_config = ConfigDict(from_attributes=True)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.lead import LeadStatus, LeadPriority
from app.schemas.contact import ContactSummary


class LeadBase(BaseModel):
    clinic_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None
    status: Optional[LeadStatus] = LeadStatus.NEW
    priority: Optional[LeadPriority] = LeadPriority.MEDIUM
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    next_followup: Optional[datetime] = None


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
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    next_followup: Optional[datetime] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    # Uncomment later if you want contacts returned with leads
    # contacts: list[ContactSummary] = []

    model_config = ConfigDict(from_attributes=True)
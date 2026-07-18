from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    lead_id: int
    name: str
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact: Optional[str] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(ContactBase):
    id: int
    assigned_to: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactSummary(BaseModel):
    id: int
    name: str
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
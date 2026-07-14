from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OpportunityBase(BaseModel):
    name: str
    clinic_name: str
    estimated_value: float = 0
    stage: str = "Qualification"
    probability: int = 10
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None
    lead_id: Optional[int] = None
    assigned_to: Optional[int] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    clinic_name: Optional[str] = None
    estimated_value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None


class OpportunityResponse(OpportunityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ClientBase(BaseModel):
    client_name: str
    lead_id: int
    opportunity_id: int
    proposal_id: int

    account_manager_id: Optional[int] = None

    pricing_model: str

    monthly_revenue: float = 0

    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None

    status: str = "ACTIVE"

    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    client_name: Optional[str] = None
    account_manager_id: Optional[int] = None

    pricing_model: Optional[str] = None
    monthly_revenue: Optional[float] = None

    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None

    status: Optional[str] = None

    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
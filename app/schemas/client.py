from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    proposal_id: int
    client_name: str
    pricing_model: str
    monthly_revenue: float = 0
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: str = "Active"
    account_manager_id: Optional[int] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    client_name: Optional[str] = None
    pricing_model: Optional[str] = None
    monthly_revenue: Optional[float] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: Optional[str] = None
    account_manager_id: Optional[int] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
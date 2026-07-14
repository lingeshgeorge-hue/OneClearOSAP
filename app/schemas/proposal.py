from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProposalBase(BaseModel):
    opportunity_id: int
    pricing_model: str
    proposed_value: float
    contract_duration: int = 12
    status: str = "Draft"
    notes: Optional[str] = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    pricing_model: Optional[str] = None
    proposed_value: Optional[float] = None
    contract_duration: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ProposalResponse(ProposalBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.pricing_model import PricingModel
from app.core.proposal_status import ProposalStatus


class ProposalBase(BaseModel):
    opportunity_id: int

    pricing_model: PricingModel

    # Draft/generated proposals may initially have a value of 0.
    pricing_value: float = Field(
        default=0,
        ge=0,
    )

    services: Optional[str] = None

    monthly_revenue: float = Field(
        default=0,
        ge=0,
    )

    annual_revenue: float = Field(
        default=0,
        ge=0,
    )

    contract_duration: int = Field(
        default=12,
        ge=1,
    )

    status: ProposalStatus = ProposalStatus.DRAFT

    notes: Optional[str] = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    pricing_model: Optional[PricingModel] = None

    pricing_value: Optional[float] = Field(
        default=None,
        ge=0,
    )

    services: Optional[str] = None

    monthly_revenue: Optional[float] = Field(
        default=None,
        ge=0,
    )

    annual_revenue: Optional[float] = Field(
        default=None,
        ge=0,
    )

    contract_duration: Optional[int] = Field(
        default=None,
        ge=1,
    )

    status: Optional[ProposalStatus] = None

    notes: Optional[str] = None


class ProposalResponse(ProposalBase):
    id: int

    proposal_number: str

    version: int

    assigned_to: Optional[int] = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
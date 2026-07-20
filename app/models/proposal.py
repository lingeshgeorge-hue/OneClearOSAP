from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base

from app.core.pricing_model import PricingModel
from app.core.proposal_status import ProposalStatus


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)

    proposal_number = Column(
        String,
        unique=True,
        nullable=False,
    )

    version = Column(
        Integer,
        default=1,
    )

    opportunity_id = Column(
        Integer,
        ForeignKey("opportunities.id"),
        nullable=False,
    )

    pricing_model = Column(
        String,
        nullable=False,
    )

    pricing_value = Column(
        Float,
        nullable=False,
    )

    services = Column(Text)

    monthly_revenue = Column(
        Float,
        default=0,
    )

    annual_revenue = Column(
        Float,
        default=0,
    )

    contract_duration = Column(
        Integer,
        default=12,
    )

    status = Column(
        String,
        default=ProposalStatus.DRAFT.value,
    )

    notes = Column(Text)

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    opportunity = relationship(
        "Opportunity",
        back_populates="proposals",
    )

    owner = relationship(
        "User",
    )
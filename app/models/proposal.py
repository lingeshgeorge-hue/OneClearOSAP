from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)

    opportunity_id = Column(
        Integer,
        ForeignKey("opportunities.id"),
        nullable=False
    )

    pricing_model = Column(
        String,
        nullable=False
    )  # Collections, Hourly, FTE

    proposed_value = Column(
        Float,
        nullable=False
    )

    contract_duration = Column(
        Integer,
        default=12
    )  # Months

    status = Column(
        String,
        default="Draft"
    )

    notes = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    opportunity = relationship("Opportunity")
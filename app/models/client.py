from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    client_name = Column(
        String,
        nullable=False,
    )

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False,
    )

    opportunity_id = Column(
        Integer,
        ForeignKey("opportunities.id"),
        nullable=False,
    )

    proposal_id = Column(
        Integer,
        ForeignKey("proposals.id"),
        nullable=False,
    )

    account_manager_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    pricing_model = Column(
        String,
        nullable=False,
    )

    monthly_revenue = Column(
        Float,
        default=0,
    )

    contract_start_date = Column(
        Date,
        nullable=True,
    )

    contract_end_date = Column(
        Date,
        nullable=True,
    )

    status = Column(
        String,
        default="ACTIVE",
    )

    notes = Column(
        Text,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    lead = relationship(
        "Lead"
    )

    opportunity = relationship(
        "Opportunity"
    )

    proposal = relationship(
        "Proposal"
    )

    account_manager = relationship(
        "User"
    )
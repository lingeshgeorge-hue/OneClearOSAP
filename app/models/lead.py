from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database.database import Base


class LeadPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class LeadStatus(str, enum.Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    clinic_name = Column(String, nullable=False)
    contact_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String)
    specialty = Column(String)
    state = Column(String)
    source = Column(String)
    status = Column(
    Enum(LeadStatus),
    default=LeadStatus.NEW,
    nullable=False
)
    notes = Column(String)
    next_followup = Column(DateTime, nullable=True)
    priority = Column(
    Enum(LeadPriority),
    default=LeadPriority.MEDIUM,
    nullable=False
)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    assigned_user = relationship("User")

    contacts = relationship(
        "Contact",
        back_populates="lead",
        cascade="all, delete-orphan"
    )

    activities = relationship(
    "Activity",
    back_populates="lead",
    cascade="all, delete-orphan"
)
    
    opportunities = relationship(
    "Opportunity",
    back_populates="lead",
    cascade="all, delete-orphan"
)
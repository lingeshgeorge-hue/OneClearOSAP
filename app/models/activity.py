from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False
    )

    activity_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    lead = relationship(
        "Lead",
        back_populates="activities"
    )

    user = relationship(
        "User"
    )
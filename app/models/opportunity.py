from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    clinic_name = Column(String, nullable=False)

    estimated_value = Column(Float, default=0)

    stage = Column(String, default="Qualification")

    probability = Column(Integer, default=10)

    expected_close_date = Column(DateTime)

    notes = Column(Text)

    lead_id = Column(Integer, ForeignKey("leads.id"))

    assigned_to = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead")
    owner = relationship("User")
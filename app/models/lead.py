from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.database import Base
from sqlalchemy.orm import relationship


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

    status = Column(String, default="New")

    assigned_to = Column(String)

    notes = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship(
    "Contact",
    back_populates="lead",
    cascade="all, delete-orphan"
)
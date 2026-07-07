from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    designation = Column(String)

    email = Column(String)

    phone = Column(String)

    preferred_contact = Column(String)

    notes = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    lead = relationship(
    "Lead",
    back_populates="contacts"
)
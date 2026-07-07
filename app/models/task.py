from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False,
    )

    contact_id = Column(
        Integer,
        ForeignKey("contacts.id"),
        nullable=True,
    )

    title = Column(String, nullable=False)

    description = Column(String)

    due_date = Column(DateTime)

    priority = Column(String, default="Medium")

    status = Column(String, default="Pending")

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    lead = relationship("Lead")

    contact = relationship("Contact")
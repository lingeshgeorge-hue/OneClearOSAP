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

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(String)

    due_date = Column(DateTime)

    priority = Column(
        String,
        default="Medium",
    )

    status = Column(
        String,
        default="Pending",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    lead = relationship("Lead")

    contact = relationship("Contact")

    assigned_user = relationship("User")
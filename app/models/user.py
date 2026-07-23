from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String)

    email = Column(String, unique=True)

    hashed_password = Column(String)

    role = Column(
        String,
        nullable=False,
        default="agent"
    )

    # Organizational reporting hierarchy
    # Example:
    # Admin -> Manager -> Sales Agent
    manager_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    manager = relationship(
        "User",
        remote_side=[id],
        back_populates="team_members",
        foreign_keys=[manager_id],
    )

    team_members = relationship(
        "User",
        back_populates="manager",
        foreign_keys=[manager_id],
    )

    # Assigned Contacts
    contacts = relationship(
        "Contact",
        back_populates="assigned_user",
        foreign_keys="Contact.assigned_to"
    )

    # Assigned Opportunities
    opportunities = relationship(
        "Opportunity",
        back_populates="owner"
    )

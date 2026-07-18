from sqlalchemy import Column, Integer, String

from app.database.database import Base

from sqlalchemy import Column, String

from sqlalchemy.orm import relationship, Session


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
    
    contacts = relationship(
    "Contact",
    back_populates="assigned_user"
)
    
    role = Column(String, nullable=False, default="agent")
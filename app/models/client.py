from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)

    proposal_id = Column(
        Integer,
        ForeignKey("proposals.id"),
        nullable=False
    )

    client_name = Column(
        String,
        nullable=False
    )

    pricing_model = Column(
        String,
        nullable=False
    )

    monthly_revenue = Column(
        Float,
        default=0
    )

    contract_start_date = Column(Date)

    contract_end_date = Column(Date)

    status = Column(
        String,
        default="Active"
    )

    account_manager_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    proposal = relationship("Proposal")
    account_manager = relationship("User")
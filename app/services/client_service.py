from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.proposal import Proposal


def get_proposal_or_none(
    db: Session,
    proposal_id: int,
):
    return (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id
        )
        .first()
    )


def calculate_annual_revenue(
    monthly_revenue: float,
):
    return monthly_revenue * 12


def calculate_contract_value(
    monthly_revenue: float,
    start_date,
    end_date,
):
    """
    Placeholder for future enhancement.
    Currently returns annual revenue.
    """

    return calculate_annual_revenue(
        monthly_revenue
    )
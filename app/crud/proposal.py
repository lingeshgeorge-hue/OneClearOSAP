from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
)

from app.services.proposal_service import (
    generate_proposal_number,
    get_next_version,
    get_opportunity_or_none,
)


def create_proposal_from_opportunity(
    db: Session,
    opportunity_id: int,
    user_id: int,
):
    """
    Generate a new proposal directly from an existing opportunity.
    """

    opportunity = get_opportunity_or_none(
        db,
        opportunity_id,
    )

    if not opportunity:
        return None

    proposal = Proposal(
        proposal_number=generate_proposal_number(db),
        version=get_next_version(
            db,
            opportunity.id,
        ),
        opportunity_id=opportunity.id,
        pricing_model="Percentage",
        pricing_value=0,
        services="",
        monthly_revenue=0,
        annual_revenue=0,
        contract_duration=12,
        status="Draft",
        notes="Generated from Opportunity",
        assigned_to=user_id,
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return proposal


def create_proposal(
    db: Session,
    proposal: ProposalCreate,
    user_id: int,
):
    """
    Create a proposal manually.
    """

    opportunity = get_opportunity_or_none(
        db,
        proposal.opportunity_id,
    )

    if not opportunity:
        return None

    proposal_data = proposal.model_dump()

    proposal_data["annual_revenue"] = (
        proposal_data.get("monthly_revenue", 0) * 12
    )

    proposal_data["proposal_number"] = (
        generate_proposal_number(db)
    )

    proposal_data["version"] = (
        get_next_version(
            db,
            proposal.opportunity_id,
        )
    )

    proposal_data["assigned_to"] = user_id

    db_proposal = Proposal(
        **proposal_data
    )

    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)

    return db_proposal


def get_all_proposals(
    db: Session,
):
    return (
        db.query(Proposal)
        .order_by(Proposal.id.desc())
        .all()
    )


def get_proposals_by_assignee(
    db: Session,
    user_id: int,
):
    return (
        db.query(Proposal)
        .filter(
            Proposal.assigned_to == user_id
        )
        .order_by(Proposal.id.desc())
        .all()
    )


def get_proposal(
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


def update_proposal(
    db: Session,
    proposal_id: int,
    proposal: ProposalUpdate,
):
    db_proposal = get_proposal(
        db,
        proposal_id,
    )

    if not db_proposal:
        return None

    update_data = proposal.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_proposal,
            key,
            value,
        )

    # Keep annual revenue synchronized whenever
    # monthly revenue changes.
    if "monthly_revenue" in update_data:
        db_proposal.annual_revenue = (
            db_proposal.monthly_revenue * 12
        )

    db.commit()
    db.refresh(db_proposal)

    return db_proposal


def delete_proposal(
    db: Session,
    proposal_id: int,
):
    db_proposal = get_proposal(
        db,
        proposal_id,
    )

    if not db_proposal:
        return None

    db.delete(db_proposal)
    db.commit()

    return db_proposal
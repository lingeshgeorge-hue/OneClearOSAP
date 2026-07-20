from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.models.lead import Lead, LeadStatus

from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
)

from app.services.proposal_service import (
    generate_proposal_number,
    get_next_version,
    get_opportunity_or_none,
)


def _move_lead_to_proposal_sent(
    db: Session,
    lead_id: int,
):
    """
    Move the linked Lead to PROPOSAL_SENT.

    WON and LOST are terminal states and must
    never be moved backwards.
    """

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )

    if not lead:
        return None

    if lead.status not in [
        LeadStatus.WON,
        LeadStatus.LOST,
    ]:
        lead.status = LeadStatus.PROPOSAL_SENT

    return lead


def create_proposal_from_opportunity(
    db: Session,
    opportunity_id: int,
    user_id: int,
):
    """
    Generate a Proposal from an existing Opportunity.

    Lifecycle automation:
    Creating the Proposal automatically moves the
    linked Lead to PROPOSAL_SENT.

    Proposal creation and Lead status update are
    committed in one database transaction.
    """

    # -------------------------------------------------
    # 1. Verify Opportunity exists
    # -------------------------------------------------

    opportunity = get_opportunity_or_none(
        db,
        opportunity_id,
    )

    if not opportunity:
        return None

    # -------------------------------------------------
    # 2. Prepare Proposal
    # -------------------------------------------------

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

    try:

        # -------------------------------------------------
        # 3. Add Proposal
        # -------------------------------------------------

        db.add(proposal)

        # -------------------------------------------------
        # 4. Lifecycle automation
        # Opportunity -> Lead -> PROPOSAL_SENT
        # -------------------------------------------------

        _move_lead_to_proposal_sent(
            db,
            opportunity.lead_id,
        )

        # -------------------------------------------------
        # 5. Commit everything together
        # -------------------------------------------------

        db.commit()

        db.refresh(proposal)

        return proposal

    except Exception:

        db.rollback()

        raise


def create_proposal(
    db: Session,
    proposal: ProposalCreate,
    user_id: int,
):
    """
    Create a Proposal manually.

    Manual Proposal creation also advances the linked
    Lead to PROPOSAL_SENT.
    """

    # -------------------------------------------------
    # 1. Verify Opportunity exists
    # -------------------------------------------------

    opportunity = get_opportunity_or_none(
        db,
        proposal.opportunity_id,
    )

    if not opportunity:
        return None

    # -------------------------------------------------
    # 2. Prepare Proposal data
    # -------------------------------------------------

    proposal_data = proposal.model_dump()

    proposal_data["annual_revenue"] = (
        proposal_data.get(
            "monthly_revenue",
            0,
        )
        * 12
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

    try:

        # -------------------------------------------------
        # 3. Add Proposal
        # -------------------------------------------------

        db.add(db_proposal)

        # -------------------------------------------------
        # 4. Lifecycle automation
        # -------------------------------------------------

        _move_lead_to_proposal_sent(
            db,
            opportunity.lead_id,
        )

        # -------------------------------------------------
        # 5. Commit together
        # -------------------------------------------------

        db.commit()

        db.refresh(db_proposal)

        return db_proposal

    except Exception:

        db.rollback()

        raise


def get_all_proposals(
    db: Session,
):
    return (
        db.query(Proposal)
        .order_by(
            Proposal.id.desc()
        )
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
        .order_by(
            Proposal.id.desc()
        )
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
    """
    Update an existing Proposal.

    Annual revenue is automatically recalculated
    whenever monthly revenue changes.
    """

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
            db_proposal.monthly_revenue
            * 12
        )

    try:

        db.commit()

        db.refresh(db_proposal)

        return db_proposal

    except Exception:

        db.rollback()

        raise


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

    try:

        db.delete(db_proposal)

        db.commit()

        return db_proposal

    except Exception:

        db.rollback()

        raise
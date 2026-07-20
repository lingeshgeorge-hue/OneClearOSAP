from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.models.lead import (
    Lead,
    LeadStatus,
)

from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
)

from app.services.proposal_service import (
    generate_proposal_number,
    get_next_version,
    get_opportunity_or_none,
    proposal_exists_for_opportunity,
)


def _move_lead_to_proposal_sent(
    db: Session,
    opportunity,
):
    """
    Move the linked Lead to PROPOSAL_SENT.

    Do not move WON or LOST leads backwards
    in the lifecycle.
    """

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == opportunity.lead_id
        )
        .first()
    )

    if (
        lead
        and lead.status not in [
            LeadStatus.WON,
            LeadStatus.LOST,
        ]
    ):
        lead.status = (
            LeadStatus.PROPOSAL_SENT
        )


def create_proposal_from_opportunity(
    db: Session,
    opportunity_id: int,
    user_id: int,
):
    """
    Generate the INITIAL Proposal directly
    from an existing Opportunity.

    This endpoint is for initial generation only.

    Returns:
        ("success", proposal)
        ("opportunity_not_found", None)
        ("proposal_already_exists", existing_proposal)
    """

    # -------------------------------------------------
    # 1. Verify Opportunity
    # -------------------------------------------------

    opportunity = get_opportunity_or_none(
        db,
        opportunity_id,
    )

    if not opportunity:

        return (
            "opportunity_not_found",
            None,
        )

    # -------------------------------------------------
    # 2. Prevent accidental duplicate generation
    # -------------------------------------------------

    if proposal_exists_for_opportunity(
        db,
        opportunity_id,
    ):

        existing_proposal = (
            db.query(Proposal)
            .filter(
                Proposal.opportunity_id
                == opportunity_id
            )
            .order_by(
                Proposal.version.desc(),
                Proposal.id.desc(),
            )
            .first()
        )

        return (
            "proposal_already_exists",
            existing_proposal,
        )

    # -------------------------------------------------
    # 3. Build initial Proposal
    # -------------------------------------------------

    proposal = Proposal(
        proposal_number=(
            generate_proposal_number(db)
        ),
        version=1,
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

        db.add(proposal)

        # Lifecycle automation
        _move_lead_to_proposal_sent(
            db,
            opportunity,
        )

        db.commit()

        db.refresh(proposal)

        return (
            "success",
            proposal,
        )

    except Exception:

        db.rollback()

        raise


def create_proposal(
    db: Session,
    proposal: ProposalCreate,
    user_id: int,
):
    """
    Create the INITIAL Proposal manually.

    Manual creation must not bypass duplicate
    proposal protection.

    Returns:
        ("success", proposal)
        ("opportunity_not_found", None)
        ("proposal_already_exists", existing_proposal)
    """

    # -------------------------------------------------
    # 1. Verify Opportunity
    # -------------------------------------------------

    opportunity = get_opportunity_or_none(
        db,
        proposal.opportunity_id,
    )

    if not opportunity:

        return (
            "opportunity_not_found",
            None,
        )

    # -------------------------------------------------
    # 2. Prevent duplicate initial Proposal
    # -------------------------------------------------

    if proposal_exists_for_opportunity(
        db,
        proposal.opportunity_id,
    ):

        existing_proposal = (
            db.query(Proposal)
            .filter(
                Proposal.opportunity_id
                == proposal.opportunity_id
            )
            .order_by(
                Proposal.version.desc(),
                Proposal.id.desc(),
            )
            .first()
        )

        return (
            "proposal_already_exists",
            existing_proposal,
        )

    # -------------------------------------------------
    # 3. Prepare Proposal
    # -------------------------------------------------

    proposal_data = (
        proposal.model_dump()
    )

    monthly_revenue = (
        proposal_data.get(
            "monthly_revenue"
        )
        or 0
    )

    proposal_data["monthly_revenue"] = (
        monthly_revenue
    )

    proposal_data["annual_revenue"] = (
        monthly_revenue * 12
    )

    proposal_data["proposal_number"] = (
        generate_proposal_number(db)
    )

    # Initial proposal is always version 1.
    proposal_data["version"] = 1

    # Always use authenticated user.
    proposal_data["assigned_to"] = (
        user_id
    )

    db_proposal = Proposal(
        **proposal_data
    )

    try:

        db.add(db_proposal)

        # Lifecycle automation
        _move_lead_to_proposal_sent(
            db,
            opportunity,
        )

        db.commit()

        db.refresh(db_proposal)

        return (
            "success",
            db_proposal,
        )

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
            Proposal.assigned_to
            == user_id
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
            Proposal.id
            == proposal_id
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

    update_data = (
        proposal.model_dump(
            exclude_unset=True
        )
    )

    # These system-controlled fields should
    # never be changed through normal update.
    update_data.pop(
        "proposal_number",
        None,
    )

    update_data.pop(
        "version",
        None,
    )

    update_data.pop(
        "opportunity_id",
        None,
    )

    for key, value in update_data.items():

        setattr(
            db_proposal,
            key,
            value,
        )

    # Keep annual revenue synchronized.
    if "monthly_revenue" in update_data:

        monthly_revenue = (
            db_proposal.monthly_revenue
            or 0
        )

        db_proposal.annual_revenue = (
            monthly_revenue * 12
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

def create_proposal_revision(
    db: Session,
    proposal_id: int,
    user_id: int,
):
    """
    Create a new revision of an existing Proposal.

    Rules:
    - Source Proposal must exist.
    - Only the latest Proposal version may be revised.
    - Accepted, Rejected, and Expired Proposals
      cannot be revised.
    - Commercial details are copied.
    - New Proposal gets:
        * new proposal number
        * incremented version
        * Draft status

    Returns:
        ("success", new_proposal)
        ("proposal_not_found", None)
        ("not_latest_version", latest_proposal)
        ("revision_not_allowed", source_proposal)
    """

    # -------------------------------------------------
    # 1. Find source Proposal
    # -------------------------------------------------

    source_proposal = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id
        )
        .first()
    )

    if not source_proposal:

        return (
            "proposal_not_found",
            None,
        )

    # -------------------------------------------------
    # 2. Find latest version for Opportunity
    # -------------------------------------------------

    latest_proposal = (
        db.query(Proposal)
        .filter(
            Proposal.opportunity_id
            == source_proposal.opportunity_id
        )
        .order_by(
            Proposal.version.desc(),
            Proposal.id.desc(),
        )
        .first()
    )

    # Only latest version may be revised.
    if (
        latest_proposal
        and latest_proposal.id
        != source_proposal.id
    ):

        return (
            "not_latest_version",
            latest_proposal,
        )

    # -------------------------------------------------
    # 3. Prevent revisions of terminal Proposals
    # -------------------------------------------------

    non_revisable_statuses = [
        "Accepted",
        "Rejected",
        "Expired",
    ]

    if (
        source_proposal.status
        in non_revisable_statuses
    ):

        return (
            "revision_not_allowed",
            source_proposal,
        )

    # -------------------------------------------------
    # 4. Calculate next version
    # -------------------------------------------------

    next_version = get_next_version(
        db,
        source_proposal.opportunity_id,
    )

    # -------------------------------------------------
    # 5. Create new Proposal revision
    # -------------------------------------------------

    new_proposal = Proposal(

        proposal_number=(
            generate_proposal_number(db)
        ),

        version=next_version,

        opportunity_id=(
            source_proposal.opportunity_id
        ),

        pricing_model=(
            source_proposal.pricing_model
        ),

        pricing_value=(
            source_proposal.pricing_value
        ),

        services=(
            source_proposal.services
        ),

        monthly_revenue=(
            source_proposal.monthly_revenue
            or 0
        ),

        annual_revenue=(
            source_proposal.annual_revenue
            or 0
        ),

        contract_duration=(
            source_proposal.contract_duration
            or 12
        ),

        status="Draft",

        notes=(
            f"Revision V{next_version} "
            f"created from "
            f"{source_proposal.proposal_number} "
            f"V{source_proposal.version}"
        ),

        assigned_to=(
            source_proposal.assigned_to
            if source_proposal.assigned_to
            is not None
            else user_id
        ),
    )

    try:

        db.add(new_proposal)

        db.commit()

        db.refresh(new_proposal)

        return (
            "success",
            new_proposal,
        )

    except Exception:

        db.rollback()

        raise

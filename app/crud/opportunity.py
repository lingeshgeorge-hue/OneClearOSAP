from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.lead import Lead, LeadStatus

from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
)


CLOSED_OPPORTUNITY_STAGES = [
    "Won",
    "Lost",
]


def create_opportunity(
    db: Session,
    opportunity: OpportunityCreate,
    user_id: int,
):
    """
    Create an Opportunity from an existing Lead.

    Validation:
    - Lead must exist.
    - A Lead cannot have more than one active Opportunity.

    Lifecycle:
    - Creating an Opportunity moves the Lead to QUALIFIED.
    - WON and LOST Leads are not moved backwards.

    Returns:
        ("success", opportunity)
        ("lead_not_found", None)
        ("active_opportunity_exists", existing_opportunity)
    """

    # -------------------------------------------------
    # 1. Verify Lead exists
    # -------------------------------------------------

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == opportunity.lead_id
        )
        .first()
    )

    if not lead:
        return (
            "lead_not_found",
            None,
        )

    # -------------------------------------------------
    # 2. Prevent duplicate active Opportunity
    # -------------------------------------------------

    existing_active_opportunity = (
        db.query(Opportunity)
        .filter(
            Opportunity.lead_id
            == opportunity.lead_id,
            Opportunity.stage.notin_(
                CLOSED_OPPORTUNITY_STAGES
            ),
        )
        .first()
    )

    if existing_active_opportunity:
        return (
            "active_opportunity_exists",
            existing_active_opportunity,
        )

    # -------------------------------------------------
    # 3. Prepare Opportunity
    # -------------------------------------------------

    opportunity_data = (
        opportunity.model_dump()
    )

    # Always assign authenticated creator.
    # Do not trust assigned_to supplied by request.
    opportunity_data["assigned_to"] = (
        user_id
    )

    db_opportunity = Opportunity(
        **opportunity_data
    )

    try:

        # -------------------------------------------------
        # 4. Create Opportunity
        # -------------------------------------------------

        db.add(db_opportunity)

        # -------------------------------------------------
        # 5. Lifecycle automation
        # -------------------------------------------------

        if lead.status not in [
            LeadStatus.WON,
            LeadStatus.LOST,
        ]:
            lead.status = (
                LeadStatus.QUALIFIED
            )

        # -------------------------------------------------
        # 6. Commit both changes together
        # -------------------------------------------------

        db.commit()

        db.refresh(db_opportunity)
        db.refresh(lead)

        return (
            "success",
            db_opportunity,
        )

    except Exception:

        db.rollback()

        raise


def get_opportunities(
    db: Session,
):
    return (
        db.query(Opportunity)
        .order_by(
            Opportunity.id.desc()
        )
        .all()
    )


def get_opportunities_by_assignee(
    db: Session,
    user_id: int,
):
    return (
        db.query(Opportunity)
        .filter(
            Opportunity.assigned_to
            == user_id
        )
        .order_by(
            Opportunity.id.desc()
        )
        .all()
    )


def get_opportunities_by_lead(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Opportunity)
        .filter(
            Opportunity.lead_id
            == lead_id
        )
        .order_by(
            Opportunity.id.desc()
        )
        .all()
    )


def get_opportunity(
    db: Session,
    opportunity_id: int,
):
    return (
        db.query(Opportunity)
        .filter(
            Opportunity.id
            == opportunity_id
        )
        .first()
    )


def update_opportunity(
    db: Session,
    opportunity_id: int,
    opportunity: OpportunityUpdate,
):
    db_opportunity = get_opportunity(
        db,
        opportunity_id,
    )

    if not db_opportunity:
        return None

    update_data = (
        opportunity.model_dump(
            exclude_unset=True
        )
    )

    for key, value in update_data.items():

        setattr(
            db_opportunity,
            key,
            value,
        )

    try:

        db.commit()

        db.refresh(db_opportunity)

        return db_opportunity

    except Exception:

        db.rollback()

        raise


def delete_opportunity(
    db: Session,
    opportunity_id: int,
):
    db_opportunity = get_opportunity(
        db,
        opportunity_id,
    )

    if not db_opportunity:
        return None

    try:

        db.delete(db_opportunity)

        db.commit()

        return db_opportunity

    except Exception:

        db.rollback()

        raise
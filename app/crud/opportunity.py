from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.lead import Lead, LeadStatus

from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
)


def create_opportunity(
    db: Session,
    opportunity: OpportunityCreate,
    user_id: int,
):
    """
    Create an Opportunity from an existing Lead.

    Lifecycle automation:
    When an Opportunity is successfully created,
    the linked Lead automatically moves to QUALIFIED.

    Opportunity creation and Lead status update
    are committed in one transaction.
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
        return None

    # -------------------------------------------------
    # 2. Prepare Opportunity
    # -------------------------------------------------

    opportunity_data = opportunity.model_dump()

    # Automatically assign the Opportunity
    # to the authenticated user creating it.
    opportunity_data["assigned_to"] = user_id

    db_opportunity = Opportunity(
        **opportunity_data
    )

    try:

        # -------------------------------------------------
        # 3. Create Opportunity
        # -------------------------------------------------

        db.add(db_opportunity)

        # -------------------------------------------------
        # 4. Lifecycle automation
        #
        # Do not move WON or LOST leads backwards.
        # -------------------------------------------------

        if lead.status not in [
            LeadStatus.WON,
            LeadStatus.LOST,
        ]:
            lead.status = LeadStatus.QUALIFIED

        # -------------------------------------------------
        # 5. Commit both changes together
        # -------------------------------------------------

        db.commit()

        db.refresh(db_opportunity)
        db.refresh(lead)

        return db_opportunity

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
            Opportunity.assigned_to == user_id
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
            Opportunity.lead_id == lead_id
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
            Opportunity.id == opportunity_id
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

    update_data = opportunity.model_dump(
        exclude_unset=True
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
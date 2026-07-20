from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.lead import Lead
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
)


def create_opportunity(
    db: Session,
    opportunity: OpportunityCreate,
    user_id: int,
):
    # Verify Lead Exists
    lead = (
        db.query(Lead)
        .filter(Lead.id == opportunity.lead_id)
        .first()
    )

    if not lead:
        return None

    opportunity_data = opportunity.model_dump()

    # Automatically assign creator
    opportunity_data["assigned_to"] = user_id

    db_opportunity = Opportunity(**opportunity_data)

    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


def get_opportunities(db: Session):
    return db.query(Opportunity).all()


def get_opportunities_by_assignee(
    db: Session,
    user_id: int,
):
    return (
        db.query(Opportunity)
        .filter(Opportunity.assigned_to == user_id)
        .all()
    )


def get_opportunities_by_lead(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Opportunity)
        .filter(Opportunity.lead_id == lead_id)
        .all()
    )


def get_opportunity(
    db: Session,
    opportunity_id: int,
):
    return (
        db.query(Opportunity)
        .filter(Opportunity.id == opportunity_id)
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
        setattr(db_opportunity, key, value)

    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


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

    db.delete(db_opportunity)
    db.commit()

    return db_opportunity
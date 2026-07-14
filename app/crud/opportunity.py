from sqlalchemy.orm import Session
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate


def create_opportunity(
    db: Session,
    opportunity: OpportunityCreate
):
    db_opportunity = Opportunity(**opportunity.model_dump())

    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


def get_opportunities(db: Session):
    return db.query(Opportunity).all()


def get_opportunity(
    db: Session,
    opportunity_id: int
):
    return (
        db.query(Opportunity)
        .filter(Opportunity.id == opportunity_id)
        .first()
    )


def delete_opportunity(
    db: Session,
    opportunity_id: int
):
    opportunity = get_opportunity(db, opportunity_id)

    if opportunity:
        db.delete(opportunity)
        db.commit()

    return opportunity

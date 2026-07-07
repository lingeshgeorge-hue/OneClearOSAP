from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(**lead.model_dump())

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    return db_lead


def get_all_leads(db: Session):
    return db.query(Lead).all()


def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead(db: Session, lead_id: int, lead: LeadUpdate):
    db_lead = get_lead_by_id(db, lead_id)

    if not db_lead:
        return None

    update_data = lead.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_lead, key, value)

    db.commit()
    db.refresh(db_lead)

    return db_lead


def delete_lead(db: Session, lead_id: int):
    db_lead = get_lead_by_id(db, lead_id)

    if not db_lead:
        return None

    db.delete(db_lead)
    db.commit()

    return db_lead
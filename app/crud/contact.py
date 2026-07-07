from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.lead import Lead
from app.schemas.contact import ContactCreate, ContactUpdate


def create_contact(db: Session, contact: ContactCreate):
    # Verify the lead exists
    lead = db.query(Lead).filter(Lead.id == contact.lead_id).first()

    if not lead:
        return None

    db_contact = Contact(**contact.model_dump())

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


def get_all_contacts(db: Session):
    return db.query(Contact).all()


def get_contact_by_id(db: Session, contact_id: int):
    return db.query(Contact).filter(Contact.id == contact_id).first()


def update_contact(
    db: Session,
    contact_id: int,
    contact: ContactUpdate,
):
    db_contact = get_contact_by_id(db, contact_id)

    if not db_contact:
        return None

    update_data = contact.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)

    return db_contact


def delete_contact(
    db: Session,
    contact_id: int,
):
    db_contact = get_contact_by_id(db, contact_id)

    if not db_contact:
        return None

    db.delete(db_contact)
    db.commit()

    return db_contact
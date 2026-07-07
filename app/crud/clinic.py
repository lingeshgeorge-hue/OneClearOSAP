from sqlalchemy.orm import Session

from app.models.clinic import Clinic
from app.schemas.clinic import ClinicCreate


def create_clinic(db: Session, clinic: ClinicCreate):
    db_clinic = Clinic(**clinic.model_dump())

    db.add(db_clinic)
    db.commit()
    db.refresh(db_clinic)

    return db_clinic


def get_clinics(db: Session):
    return db.query(Clinic).all()
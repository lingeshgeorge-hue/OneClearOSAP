from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.clinic import ClinicCreate, ClinicResponse
from app.crud.clinic import create_clinic, get_clinics

from app.auth.oauth2 import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/clinics",
    tags=["Clinics"]
)


@router.post(
    "/",
    response_model=ClinicResponse
)
def create_new_clinic(
    clinic: ClinicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_clinic(db, clinic)


@router.get(
    "/",
    response_model=List[ClinicResponse]
)
def list_clinics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_clinics(db)
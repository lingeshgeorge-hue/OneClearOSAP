from fastapi import APIRouter, Depends
print("Opportunity router loaded")

from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityResponse
)
from app.crud import opportunity as crud

router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"]
)


@router.post(
    "/",
    response_model=OpportunityResponse
)
def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db)
):
    return crud.create_opportunity(db, opportunity)


@router.get(
    "/",
    response_model=List[OpportunityResponse]
)
def get_opportunities(
    db: Session = Depends(get_db)
):
    return crud.get_opportunities(db)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    return crud.get_opportunity(db, opportunity_id)


@router.delete("/{opportunity_id}")
def delete_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    return crud.delete_opportunity(db, opportunity_id)
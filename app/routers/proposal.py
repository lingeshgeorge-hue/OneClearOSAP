from fastapi import APIRouter, Depends
print("Proposal router loaded")
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db

from app.schemas.proposal import (
    ProposalCreate,
    ProposalResponse
)

from app.crud import proposal as crud

router = APIRouter(
    prefix="/proposals",
    tags=["Proposals"]
)


@router.post(
    "/",
    response_model=ProposalResponse
)
def create_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db)
):
    return crud.create_proposal(
        db,
        proposal
    )


@router.get(
    "/",
    response_model=List[ProposalResponse]
)
def get_proposals(
    db: Session = Depends(get_db)
):
    return crud.get_proposals(db)
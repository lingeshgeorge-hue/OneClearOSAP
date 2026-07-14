from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse
)

from app.crud.activity import (
    create_activity,
    get_lead_activities
)

from app.models.lead import Lead
from app.models.user import User

from app.core.security import get_current_user

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post(
    "/lead/{lead_id}",
    response_model=ActivityResponse
)
def add_activity(
    lead_id: int,
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return create_activity(
        db,
        lead_id,
        activity,
        current_user.id
    )


@router.get(
    "/lead/{lead_id}",
    response_model=list[ActivityResponse]
)
def get_activities(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_lead_activities(
        db,
        lead_id
    )
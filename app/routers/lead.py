from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
)

from app.crud.lead import (
    create_lead,
    get_all_leads,
    get_lead_by_id,
    update_lead,
    delete_lead,
)

from app.models.user import User
from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


@router.post(
    "/",
    response_model=LeadResponse
)
def create_new_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.SALES
        ])
    ),
):
    return create_lead(db, lead)


@router.get(
    "/",
    response_model=list[LeadResponse]
)
def read_all_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_leads(db)


@router.get(
    "/{lead_id}",
    response_model=LeadResponse
)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return lead


@router.put(
    "/{lead_id}",
    response_model=LeadResponse
)
def edit_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.SALES
        ])
    ),
):
    updated = update_lead(
        db,
        lead_id,
        lead
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return updated


@router.delete(
    "/{lead_id}"
)
def remove_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN
        ])
    ),
):
    deleted = delete_lead(
        db,
        lead_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return {
        "message": "Lead deleted successfully"
    }
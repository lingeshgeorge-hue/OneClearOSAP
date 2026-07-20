from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User
from app.models.lead import Lead

from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
)

from app.schemas.assignment import AssignRequest

from app.crud.lead import (
    create_lead,
    get_all_leads,
    get_lead_by_id,
    update_lead,
    delete_lead,
)

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


# ============================================================
# CREATE LEAD
# Admin / Manager
# ============================================================

@router.post(
    "/",
    response_model=LeadResponse,
)
def create_new_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    result, new_lead = create_lead(
        db,
        lead,
    )

    if result == "duplicate_email":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A lead with this email "
                "already exists"
            ),
        )

    if result == "invalid_assignee":

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if result == "database_error":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Lead could not be created "
                "because of a database constraint"
            ),
        )

    return new_lead


# ============================================================
# GET ALL LEADS
# Admin / Manager -> all
# Other users -> assigned leads only
# ============================================================

@router.get(
    "/",
    response_model=list[LeadResponse],
)
def read_all_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return get_all_leads(
        db,
        current_user,
    )


# ============================================================
# GET ONE LEAD
# ============================================================

@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    lead = get_lead_by_id(
        db,
        lead_id,
    )

    if not lead:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return lead


# ============================================================
# UPDATE LEAD
# Admin / Manager
# ============================================================

@router.put(
    "/{lead_id}",
    response_model=LeadResponse,
)
def edit_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    result, updated = update_lead(
        db,
        lead_id,
        lead,
    )

    if result == "not_found":

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    if result == "duplicate_email":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Another lead with this email "
                "already exists"
            ),
        )

    if result == "invalid_assignee":

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if result == "database_error":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Lead could not be updated "
                "because of a database constraint"
            ),
        )

    return updated


# ============================================================
# DELETE LEAD
# Admin only
# ============================================================

@router.delete(
    "/{lead_id}",
)
def remove_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):

    deleted = delete_lead(
        db,
        lead_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return {
        "message": (
            "Lead deleted successfully"
        )
    }


# ============================================================
# ASSIGN LEAD
# Admin / Manager
# ============================================================

@router.put(
    "/{lead_id}/assign",
)
def assign_lead(
    lead_id: int,
    assignment: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )

    if not lead:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    user = (
        db.query(User)
        .filter(
            User.id == assignment.user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    lead.assigned_to = user.id

    db.commit()

    db.refresh(lead)

    return {
        "message": (
            "Lead assigned successfully"
        ),
        "lead_id": lead.id,
        "assigned_user_id": user.id,
        "assigned_to": user.full_name,
    }
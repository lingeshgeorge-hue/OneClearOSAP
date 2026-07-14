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
from app.models.lead import Lead
from app.models.user import User
from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles

from app.schemas.assignment import AssignRequest
from app.models.user import User
from app.core.permissions import RoleChecker


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
    Roles.MANAGER
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
    try:
        print("=" * 50)
        print("GET LEADS CALLED")
        print("CURRENT USER:", current_user.email)
        print("CURRENT ROLE:", current_user.role)

        leads = get_all_leads(db)

        print("LEADS FOUND:", len(leads))

        return leads

    except Exception as e:
        print("GET LEADS ERROR:", type(e).__name__)
        print("ERROR MESSAGE:", str(e))
        raise
    try:
        leads = get_all_leads(db)
        print("LEADS FOUND:", leads)
        return leads
    except Exception as e:
        print("GET LEADS ERROR:", repr(e))
        raise


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
    Roles.MANAGER
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

@router.put("/{lead_id}/assign")
def assign_lead(
    lead_id: int,
    assignment: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
    RoleChecker([
        Roles.ADMIN,
        Roles.MANAGER
    ])
),
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    user = db.query(User).filter(
        User.id == assignment.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    lead.assigned_to = assignment.user_id

    db.commit()
    db.refresh(lead)

    return {
        "message": "Lead assigned successfully",
        "lead_id": lead.id,
        "assigned_to": user.full_name,
        "assigned_user_id": user.id
    }

@router.get("/")
def get_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role in ["Admin", "Manager"]:
        return db.query(Lead).all()

    return db.query(Lead).filter(
        Lead.assigned_to == current_user.id
    ).all()

@router.get("/")
def get_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(
    RoleChecker(["admin", "manager", "agent"])
),
):
    if current_user.role in ["admin", "manager"]:
        return db.query(Lead).all()

    return db.query(Lead).filter(
        Lead.assigned_to == current_user.id
    ).all()

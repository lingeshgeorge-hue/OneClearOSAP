from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    ActivitySummary,
)

from app.crud.activity import (
    create_activity,
    get_lead_by_id,
    get_lead_activities,
    get_user_activities,
    get_user_activity_summary,
)

from app.models.lead import Lead
from app.models.user import User

from app.core.security import get_current_user
from app.core.roles import Roles


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


# ============================================================
# ACCESS CONTROL HELPER
# ============================================================

def ensure_lead_access(
    lead: Lead,
    current_user: User,
):
    """
    Admin and Manager can access any lead.

    Other authenticated users can access only
    leads assigned to them.
    """

    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return

    if lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access activities for this lead"
            ),
        )


# ============================================================
# MY ACTIVITY SUMMARY
#
# IMPORTANT:
# Static routes must remain above /lead/{lead_id}.
# ============================================================

@router.get(
    "/my/summary",
    response_model=ActivitySummary,
)
def read_my_activity_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_user_activity_summary(
        db,
        current_user.id,
    )


# ============================================================
# MY ACTIVITY HISTORY
# ============================================================

@router.get(
    "/my",
    response_model=list[ActivityResponse],
)
def read_my_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_user_activities(
        db,
        current_user.id,
    )


# ============================================================
# CREATE ACTIVITY FOR LEAD
# ============================================================

@router.post(
    "/lead/{lead_id}",
    response_model=ActivityResponse,
)
def add_activity(
    lead_id: int,
    activity: ActivityCreate,
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

    ensure_lead_access(
        lead,
        current_user,
    )

    return create_activity(
        db,
        lead_id,
        activity,
        current_user.id,
    )


# ============================================================
# GET ACTIVITIES FOR LEAD
# ============================================================

@router.get(
    "/lead/{lead_id}",
    response_model=list[ActivityResponse],
)
def get_activities(
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

    ensure_lead_access(
        lead,
        current_user,
    )

    return get_lead_activities(
        db,
        lead_id,
    )

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.crud.dashboard import (
    get_dashboard_data,
    get_user_dashboard_data,
)

from app.models.user import User

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# EXECUTIVE DASHBOARD
# Admin / Manager only
# ============================================================

@router.get("/")
def dashboard(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    """
    CRM executive dashboard.

    Accessible to:
    - Admin
    - Manager

    Contains organization-wide CRM,
    pipeline, conversion, and revenue analytics.
    """

    return get_dashboard_data(db)


# ============================================================
# USER-SCOPED DASHBOARD
# Any authenticated user
# ============================================================

@router.get("/my")
def my_dashboard(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Personal CRM performance dashboard.

    Data is scoped to the authenticated user.

    Sales users see only their own:
    - Leads
    - Opportunities
    - Proposals
    - Pipeline
    - Conversions
    - Follow-ups
    - Tasks
    - Performance metrics

    Organization-wide revenue analytics
    are not exposed through this endpoint.
    """

    return get_user_dashboard_data(
        db,
        current_user.id,
    )

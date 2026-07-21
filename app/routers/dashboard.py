from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.crud.dashboard import (
    get_dashboard_data,
)

from app.models.user import User

from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


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
    """

    return get_dashboard_data(db)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.crud.dashboard import get_dashboard_metrics

from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/",
    response_model=DashboardResponse
)
def read_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_dashboard_metrics(db)
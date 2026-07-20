from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
)

from app.crud.opportunity import (
    create_opportunity,
    get_opportunities,
    get_opportunities_by_assignee,
    get_opportunities_by_lead,
    get_opportunity,
    update_opportunity,
    delete_opportunity,
)

from app.models.user import User

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


# ============================================================
# CREATE OPPORTUNITY
# ============================================================

@router.post(
    "/",
    response_model=OpportunityResponse,
)
def create_new_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    result, new_opportunity = (
        create_opportunity(
            db,
            opportunity,
            current_user.id,
        )
    )

    if result == "lead_not_found":

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Lead not found",
        )

    if result == "active_opportunity_exists":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This lead already has "
                "an active opportunity"
            ),
        )

    if result != "success":

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Opportunity creation failed"
            ),
        )

    return new_opportunity


# ============================================================
# GET ALL OPPORTUNITIES
# ============================================================

@router.get(
    "/",
    response_model=list[OpportunityResponse],
)
def read_all_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_opportunities(db)

    return get_opportunities_by_assignee(
        db,
        current_user.id,
    )


# ============================================================
# GET OPPORTUNITIES BY LEAD
#
# Keep this static route before /{opportunity_id}
# ============================================================

@router.get(
    "/lead/{lead_id}",
    response_model=list[OpportunityResponse],
)
def read_opportunities_by_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return get_opportunities_by_lead(
        db,
        lead_id,
    )


# ============================================================
# GET ONE OPPORTUNITY
# ============================================================

@router.get(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
)
def read_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    opportunity = get_opportunity(
        db,
        opportunity_id,
    )

    if not opportunity:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Opportunity not found",
        )

    return opportunity


# ============================================================
# UPDATE OPPORTUNITY
# ============================================================

@router.put(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
)
def edit_opportunity(
    opportunity_id: int,
    opportunity: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    updated = update_opportunity(
        db,
        opportunity_id,
        opportunity,
    )

    if not updated:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Opportunity not found",
        )

    return updated


# ============================================================
# DELETE OPPORTUNITY
# ============================================================

@router.delete(
    "/{opportunity_id}",
)
def remove_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):

    deleted = delete_opportunity(
        db,
        opportunity_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Opportunity not found",
        )

    return {
        "message": (
            "Opportunity deleted successfully"
        )
    }
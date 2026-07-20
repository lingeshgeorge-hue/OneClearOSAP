from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
)

from app.crud.proposal import (
    create_proposal,
    get_all_proposals,
    get_proposals_by_assignee,
    get_proposal,
    update_proposal,
    delete_proposal,
    create_proposal_from_opportunity,
    create_proposal_revision,
)

from app.models.user import User

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/proposals",
    tags=["Proposals"],
)


# ============================================================
# CREATE INITIAL PROPOSAL MANUALLY
# ============================================================

@router.post(
    "/",
    response_model=ProposalResponse,
)
def create_new_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    result, new_proposal = (
        create_proposal(
            db,
            proposal,
            current_user.id,
        )
    )

    if result == "opportunity_not_found":

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Opportunity not found",
        )

    if result == "proposal_already_exists":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This opportunity already has "
                "a proposal. Create a revision "
                "instead of another initial proposal."
            ),
        )

    if result != "success":

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Proposal creation failed",
        )

    return new_proposal


# ============================================================
# GET ALL PROPOSALS
# ============================================================

@router.get(
    "/",
    response_model=list[ProposalResponse],
)
def read_all_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_all_proposals(db)

    return get_proposals_by_assignee(
        db,
        current_user.id,
    )


# ============================================================
# GENERATE INITIAL PROPOSAL FROM OPPORTUNITY
#
# Keep static route before /{proposal_id}
# ============================================================

@router.post(
    "/from-opportunity/{opportunity_id}",
    response_model=ProposalResponse,
)
def generate_from_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
            Roles.SALES,
        ])
    ),
):

    result, proposal = (
        create_proposal_from_opportunity(
            db,
            opportunity_id,
            current_user.id,
        )
    )

    if result == "opportunity_not_found":

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Opportunity not found",
        )

    if result == "proposal_already_exists":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This opportunity already has "
                "a proposal. Create a revision "
                "instead of generating another "
                "initial proposal."
            ),
        )

    if result != "success":

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Proposal generation failed",
        )

    return proposal


# ============================================================
# GET ONE PROPOSAL
# ============================================================

# ============================================================
# CREATE PROPOSAL REVISION
#
# Keep this route before /{proposal_id}
# ============================================================

@router.post(
    "/{proposal_id}/revise",
    response_model=ProposalResponse,
)
def revise_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    result, proposal = (
        create_proposal_revision(
            db,
            proposal_id,
            current_user.id,
        )
    )

    if result == "proposal_not_found":

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Proposal not found",
        )

    if result == "not_latest_version":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only the latest proposal "
                "version can be revised"
            ),
        )

    if result == "revision_not_allowed":

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Accepted, rejected, or expired "
                "proposals cannot be revised"
            ),
        )

    if result != "success":

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Proposal revision failed"
            ),
        )

    return proposal

@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
)
def read_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    proposal = get_proposal(
        db,
        proposal_id,
    )

    if not proposal:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Proposal not found",
        )

    return proposal


# ============================================================
# UPDATE PROPOSAL
# ============================================================

@router.put(
    "/{proposal_id}",
    response_model=ProposalResponse,
)
def edit_proposal(
    proposal_id: int,
    proposal: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):

    updated = update_proposal(
        db,
        proposal_id,
        proposal,
    )

    if not updated:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Proposal not found",
        )

    return updated


# ============================================================
# DELETE PROPOSAL
# ============================================================

@router.delete(
    "/{proposal_id}",
)
def remove_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):

    deleted = delete_proposal(
        db,
        proposal_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Proposal not found",
        )

    return {
        "message": (
            "Proposal deleted successfully"
        )
    }
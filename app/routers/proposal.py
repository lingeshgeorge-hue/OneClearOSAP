from fastapi import APIRouter, Depends, HTTPException
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
)

from app.models.user import User
from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles

router = APIRouter(
    prefix="/proposals",
    tags=["Proposals"],
)


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
    new_proposal = create_proposal(
        db,
        proposal,
        current_user.id,
    )

    if not new_proposal:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return new_proposal


@router.get(
    "/",
    response_model=list[ProposalResponse],
)
def read_all_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    proposal = create_proposal_from_opportunity(
        db,
        opportunity_id,
        current_user.id,
    )

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return proposal


@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
)
def read_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    proposal = get_proposal(
        db,
        proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found",
        )

    return proposal


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
            status_code=404,
            detail="Proposal not found",
        )

    return updated


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
            status_code=404,
            detail="Proposal not found",
        )

    return {
        "message": "Proposal deleted successfully"
    }
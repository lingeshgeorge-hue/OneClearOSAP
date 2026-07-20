from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
)

from app.crud.client import (
    create_client,
    create_client_from_proposal,
    get_all_clients,
    get_clients_by_manager,
    get_client,
    update_client,
    delete_client,
)

from app.models.user import User

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


# ============================================================
# CREATE CLIENT MANUALLY
# ============================================================

@router.post(
    "/",
    response_model=ClientResponse,
)
def create_new_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    new_client = create_client(
        db,
        client,
        current_user.id,
    )

    if not new_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return new_client


# ============================================================
# AUTOMATIC PROPOSAL -> CLIENT CONVERSION
# Keep this static route before /{client_id}
# ============================================================

@router.post(
    "/from-proposal/{proposal_id}",
    response_model=ClientResponse,
)
def convert_proposal_to_client(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    conversion_status, client = (
        create_client_from_proposal(
            db,
            proposal_id,
            current_user.id,
        )
    )

    if conversion_status == "proposal_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if conversion_status == "opportunity_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Opportunity linked to proposal "
                "was not found"
            ),
        )

    if conversion_status == "lead_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Lead linked to opportunity "
                "was not found"
            ),
        )

    if conversion_status == "already_converted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This proposal has already been "
                "converted to a client"
            ),
        )

    if conversion_status != "success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Client conversion failed",
        )

    return client


# ============================================================
# GET ALL CLIENTS
# Admin / Manager -> all
# Other authenticated users -> assigned clients only
# ============================================================

@router.get(
    "/",
    response_model=list[ClientResponse],
)
def read_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_all_clients(db)

    return get_clients_by_manager(
        db,
        current_user.id,
    )


# ============================================================
# GET ONE CLIENT
# ============================================================

@router.get(
    "/{client_id}",
    response_model=ClientResponse,
)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    client = get_client(
        db,
        client_id,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return client


# ============================================================
# UPDATE CLIENT
# Admin / Manager only
# ============================================================

@router.put(
    "/{client_id}",
    response_model=ClientResponse,
)
def edit_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    updated = update_client(
        db,
        client_id,
        client,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return updated


# ============================================================
# DELETE CLIENT
# Admin only
# ============================================================

@router.delete(
    "/{client_id}",
)
def remove_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):
    deleted = delete_client(
        db,
        client_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return {
        "message": (
            "Client deleted successfully"
        )
    }
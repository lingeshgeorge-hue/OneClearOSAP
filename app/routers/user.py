from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User

from app.schemas.user import (
    UserResponse,
    ManagerAssignmentRequest,
)

from app.crud.user import (
    get_all_users,
    get_user_by_id,
    get_manager_team,
    assign_manager,
)

from app.auth.hashing import verify_password
from app.auth.jwt_handler import create_access_token

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.email == request.username
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        request.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": user.id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "manager_id": user.manager_id,
        },
    }


# ============================================================
# MY TEAM
#
# Manager:
#   Direct reports assigned through manager_id.
#
# Admin:
#   Admin has organization-wide access, but does not have
#   direct reports through the Manager -> Sales relationship.
# ============================================================

@router.get(
    "/my-team",
    response_model=list[UserResponse],
)
def read_my_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    return get_manager_team(
        db,
        current_user.id,
    )


# ============================================================
# GET TEAM FOR SPECIFIC MANAGER
# Admin only
#
# Static route is intentionally above /{user_id}.
# ============================================================

@router.get(
    "/managers/{manager_id}/team",
    response_model=list[UserResponse],
)
def read_manager_team(
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):
    manager = get_user_by_id(
        db,
        manager_id,
    )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found",
        )

    if manager.role != Roles.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected user does not have "
                "the Manager role"
            ),
        )

    return get_manager_team(
        db,
        manager.id,
    )


# ============================================================
# ASSIGN / REMOVE MANAGER
# Admin only
#
# Request:
# {
#   "manager_id": 3
# }
#
# Remove manager:
# {
#   "manager_id": null
# }
# ============================================================

@router.put(
    "/{user_id}/manager",
    response_model=UserResponse,
)
def update_user_manager(
    user_id: int,
    assignment: ManagerAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):
    result, user = assign_manager(
        db,
        user_id,
        assignment.manager_id,
    )

    if result == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if result == "manager_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found",
        )

    if result == "invalid_manager_role":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected manager must have "
                "the Manager role"
            ),
        )

    if result == "invalid_report_role":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Sales users can be assigned "
                "to a Manager"
            ),
        )

    if result == "self_assignment":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A user cannot be assigned "
                "as their own manager"
            ),
        )

    return user


# ============================================================
# GET ALL USERS
# Admin / Manager
# ============================================================

@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    return get_all_users(db)


# ============================================================
# GET ONE USER
# Admin / Manager
#
# Keep dynamic route after all static routes.
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

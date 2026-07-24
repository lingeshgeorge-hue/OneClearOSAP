from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.hashing import hash_password
from app.core.roles import Roles


def create_user(
    db: Session,
    user: UserCreate,
):
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(
            user.password
        ),
        role=user.role,
        manager_id=user.manager_id,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )


def get_all_users(
    db: Session,
):
    return (
        db.query(User)
        .order_by(
            User.id.asc()
        )
        .all()
    )


def get_manager_team(
    db: Session,
    manager_id: int,
):
    """
    Return direct reports for one manager.
    """

    return (
        db.query(User)
        .filter(
            User.manager_id == manager_id
        )
        .order_by(
            User.id.asc()
        )
        .all()
    )


def assign_manager(
    db: Session,
    user_id: int,
    manager_id: int | None,
):
    """
    Assign or remove a user's manager.

    Returns:
        ("success", user)
        ("user_not_found", None)
        ("manager_not_found", None)
        ("invalid_manager_role", None)
        ("invalid_report_role", None)
        ("self_assignment", None)
    """

    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        return (
            "user_not_found",
            None,
        )

    # Removing a manager is allowed.
    if manager_id is None:
        user.manager_id = None

        db.commit()
        db.refresh(user)

        return (
            "success",
            user,
        )

    if user.id == manager_id:
        return (
            "self_assignment",
            None,
        )

    manager = get_user_by_id(
        db,
        manager_id,
    )

    if not manager:
        return (
            "manager_not_found",
            None,
        )

    # Only a Manager can be selected
    # as a direct reporting manager.
    if manager.role != Roles.MANAGER:
        return (
            "invalid_manager_role",
            None,
        )

    # Current organizational model:
    #
    # Admin
    #   -> Manager
    #       -> Sales
    #
    # Prevent Admin or Manager accounts from
    # accidentally becoming direct reports
    # through this endpoint.
    if user.role != Roles.SALES:
        return (
            "invalid_report_role",
            None,
        )

    user.manager_id = manager.id

    db.commit()
    db.refresh(user)

    return (
        "success",
        user,
    )

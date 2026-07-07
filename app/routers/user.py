from app.core.permissions import RoleChecker
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import UserCreate, UserResponse

from app.crud.user import create_user, get_user_by_email

from app.auth.hashing import verify_password
from app.auth.jwt_handler import create_access_token
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# -----------------------------
# Register
# -----------------------------
@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin"]))
):

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return create_user(db, user)


# -----------------------------
# Login
# -----------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print("=" * 50)
    print("USERNAME RECEIVED:", repr(form_data.username))
    print("PASSWORD RECEIVED:", repr(form_data.password))
    print("=" * 50)

    db_user = get_user_by_email(db, form_data.username)

    print("USER FOUND:", db_user)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    password_ok = verify_password(form_data.password, db_user.hashed_password)
    print("PASSWORD VERIFY:", password_ok)

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "role": db_user.role
        }
    }
    # -----------------------------
# Current Logged-in User
# -----------------------------
@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role
    }
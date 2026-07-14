from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
)

from app.crud.contact import (
    create_contact,
    get_all_contacts,
    get_contact_by_id,
    update_contact,
    delete_contact,
)

from app.models.user import User
from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)


@router.post(
    "/",
    response_model=ContactResponse
)
def create_new_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    new_contact = create_contact(db, contact)

    if not new_contact:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return new_contact


@router.get(
    "/",
    response_model=list[ContactResponse]
)
def read_all_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_contacts(db)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse
)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = get_contact_by_id(db, contact_id)

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse
)
def edit_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    updated = update_contact(
        db,
        contact_id,
        contact,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return updated


@router.delete(
    "/{contact_id}"
)
def remove_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):
    deleted = delete_contact(
        db,
        contact_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return {
        "message": "Contact deleted successfully"
    }
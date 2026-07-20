from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.user import User

from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
)


def create_lead(
    db: Session,
    lead: LeadCreate,
):
    """
    Create a new lead.

    Returns:
        ("success", lead)
        ("duplicate_email", None)
        ("invalid_assignee", None)
        ("database_error", None)
    """

    # ---------------------------------------------
    # 1. Check duplicate email
    # ---------------------------------------------

    existing_lead = (
        db.query(Lead)
        .filter(
            Lead.email == lead.email
        )
        .first()
    )

    if existing_lead:
        return (
            "duplicate_email",
            None,
        )

    # ---------------------------------------------
    # 2. Validate assigned user
    # ---------------------------------------------

    if lead.assigned_to is not None:

        assigned_user = (
            db.query(User)
            .filter(
                User.id == lead.assigned_to
            )
            .first()
        )

        if not assigned_user:
            return (
                "invalid_assignee",
                None,
            )

    # ---------------------------------------------
    # 3. Create Lead
    # ---------------------------------------------

    lead_data = lead.model_dump()

    db_lead = Lead(
        **lead_data
    )

    try:
        db.add(db_lead)

        db.commit()

        db.refresh(db_lead)

        return (
            "success",
            db_lead,
        )

    except IntegrityError:

        db.rollback()

        return (
            "database_error",
            None,
        )

    except Exception:

        db.rollback()

        raise


def get_all_leads(
    db: Session,
    current_user,
):
    """
    Admin and Manager can see all leads.

    Other users only see leads
    assigned to them.
    """

    if current_user.role in [
        "Admin",
        "Manager",
    ]:
        return (
            db.query(Lead)
            .order_by(
                Lead.id.desc()
            )
            .all()
        )

    return (
        db.query(Lead)
        .filter(
            Lead.assigned_to
            == current_user.id
        )
        .order_by(
            Lead.id.desc()
        )
        .all()
    )


def get_lead_by_id(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )


def update_lead(
    db: Session,
    lead_id: int,
    lead: LeadUpdate,
):
    """
    Update an existing lead.

    Returns:
        ("success", lead)
        ("not_found", None)
        ("duplicate_email", None)
        ("invalid_assignee", None)
        ("database_error", None)
    """

    db_lead = get_lead_by_id(
        db,
        lead_id,
    )

    if not db_lead:
        return (
            "not_found",
            None,
        )

    update_data = lead.model_dump(
        exclude_unset=True
    )

    # ---------------------------------------------
    # Validate email if changed
    # ---------------------------------------------

    if (
        "email" in update_data
        and update_data["email"]
        != db_lead.email
    ):

        existing_lead = (
            db.query(Lead)
            .filter(
                Lead.email
                == update_data["email"],
                Lead.id != lead_id,
            )
            .first()
        )

        if existing_lead:
            return (
                "duplicate_email",
                None,
            )

    # ---------------------------------------------
    # Validate assigned user if changed
    # ---------------------------------------------

    if (
        "assigned_to" in update_data
        and update_data["assigned_to"]
        is not None
    ):

        assigned_user = (
            db.query(User)
            .filter(
                User.id
                == update_data[
                    "assigned_to"
                ]
            )
            .first()
        )

        if not assigned_user:
            return (
                "invalid_assignee",
                None,
            )

    for key, value in update_data.items():

        setattr(
            db_lead,
            key,
            value,
        )

    try:

        db.commit()

        db.refresh(db_lead)

        return (
            "success",
            db_lead,
        )

    except IntegrityError:

        db.rollback()

        return (
            "database_error",
            None,
        )

    except Exception:

        db.rollback()

        raise


def delete_lead(
    db: Session,
    lead_id: int,
):
    db_lead = get_lead_by_id(
        db,
        lead_id,
    )

    if not db_lead:
        return None

    db.delete(db_lead)

    db.commit()

    return db_lead
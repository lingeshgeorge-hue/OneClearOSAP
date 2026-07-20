from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.proposal import Proposal
from app.models.opportunity import Opportunity
from app.models.lead import Lead

from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
)

from app.services.client_service import (
    get_proposal_or_none,
)


def create_client(
    db: Session,
    client: ClientCreate,
    user_id: int,
):
    """
    Create a client manually.
    """

    proposal = get_proposal_or_none(
        db,
        client.proposal_id,
    )

    if not proposal:
        return None

    client_data = client.model_dump()

    if client_data["account_manager_id"] is None:
        client_data["account_manager_id"] = user_id

    db_client = Client(
        **client_data
    )

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


def create_client_from_proposal(
    db: Session,
    proposal_id: int,
    user_id: int,
):
    """
    Automatically create a Client from a Proposal.

    Workflow:

    Proposal
        ↓
    Opportunity
        ↓
    Lead
        ↓
    Client

    Returns:

    ("success", client)
    ("proposal_not_found", None)
    ("opportunity_not_found", None)
    ("lead_not_found", None)
    ("already_converted", existing_client)
    """

    # -------------------------------------------------
    # 1. Find Proposal
    # -------------------------------------------------

    proposal = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id
        )
        .first()
    )

    if not proposal:
        return (
            "proposal_not_found",
            None,
        )

    # -------------------------------------------------
    # 2. Prevent duplicate conversion
    # -------------------------------------------------

    existing_client = (
        db.query(Client)
        .filter(
            Client.proposal_id == proposal.id
        )
        .first()
    )

    if existing_client:
        return (
            "already_converted",
            existing_client,
        )

    # -------------------------------------------------
    # 3. Find linked Opportunity
    # -------------------------------------------------

    opportunity = (
        db.query(Opportunity)
        .filter(
            Opportunity.id
            == proposal.opportunity_id
        )
        .first()
    )

    if not opportunity:
        return (
            "opportunity_not_found",
            None,
        )

    # -------------------------------------------------
    # 4. Find linked Lead
    # -------------------------------------------------

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == opportunity.lead_id
        )
        .first()
    )

    if not lead:
        return (
            "lead_not_found",
            None,
        )

    # -------------------------------------------------
    # 5. Determine client name
    # -------------------------------------------------

    client_name = lead.clinic_name

    # -------------------------------------------------
    # 6. Determine monthly revenue
    # -------------------------------------------------

    monthly_revenue = (
        proposal.monthly_revenue or 0
    )

    # -------------------------------------------------
    # 7. Create Client
    # -------------------------------------------------

    db_client = Client(
        client_name=client_name,

        lead_id=lead.id,

        opportunity_id=opportunity.id,

        proposal_id=proposal.id,

        account_manager_id=(
            proposal.assigned_to
            if proposal.assigned_to is not None
            else user_id
        ),

        pricing_model=proposal.pricing_model,

        monthly_revenue=monthly_revenue,

        status="ACTIVE",

        notes=(
            f"Automatically converted from "
            f"Proposal {proposal.proposal_number}"
        ),
    )

    db.add(db_client)

    db.commit()

    db.refresh(db_client)

    return (
        "success",
        db_client,
    )


def get_all_clients(
    db: Session,
):
    """
    Return all clients.
    """

    return (
        db.query(Client)
        .order_by(
            Client.id.desc()
        )
        .all()
    )


def get_clients_by_manager(
    db: Session,
    user_id: int,
):
    """
    Return only clients assigned
    to a specific account manager.
    """

    return (
        db.query(Client)
        .filter(
            Client.account_manager_id
            == user_id
        )
        .order_by(
            Client.id.desc()
        )
        .all()
    )


def get_client(
    db: Session,
    client_id: int,
):
    """
    Return one client by ID.
    """

    return (
        db.query(Client)
        .filter(
            Client.id == client_id
        )
        .first()
    )


def update_client(
    db: Session,
    client_id: int,
    client: ClientUpdate,
):
    """
    Update an existing client.
    """

    db_client = get_client(
        db,
        client_id,
    )

    if not db_client:
        return None

    update_data = client.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_client,
            key,
            value,
        )

    db.commit()

    db.refresh(db_client)

    return db_client


def delete_client(
    db: Session,
    client_id: int,
):
    """
    Delete an existing client.
    """

    db_client = get_client(
        db,
        client_id,
    )

    if not db_client:
        return None

    db.delete(db_client)

    db.commit()

    return db_client
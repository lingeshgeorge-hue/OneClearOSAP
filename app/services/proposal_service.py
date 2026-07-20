from datetime import datetime

from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.models.opportunity import Opportunity


def generate_proposal_number(
    db: Session,
) -> str:
    """
    Generate the next proposal number.

    Format:
    OCP-YYYY-0001
    OCP-YYYY-0002

    Uses the highest existing sequence instead
    of row count so deleted records do not cause
    number reuse.
    """

    year = datetime.now().year
    prefix = f"OCP-{year}-"

    existing_numbers = (
        db.query(Proposal.proposal_number)
        .filter(
            Proposal.proposal_number.like(
                f"{prefix}%"
            )
        )
        .all()
    )

    highest_number = 0

    for row in existing_numbers:

        proposal_number = row[0]

        if not proposal_number:
            continue

        try:
            sequence = int(
                proposal_number.split("-")[-1]
            )

            highest_number = max(
                highest_number,
                sequence,
            )

        except (ValueError, IndexError):
            continue

    next_number = highest_number + 1

    return f"{prefix}{next_number:04d}"


def get_next_version(
    db: Session,
    opportunity_id: int,
) -> int:
    """
    Return the next proposal version
    for an Opportunity.
    """

    latest = (
        db.query(Proposal)
        .filter(
            Proposal.opportunity_id
            == opportunity_id
        )
        .order_by(
            Proposal.version.desc()
        )
        .first()
    )

    if (
        latest
        and latest.version is not None
    ):
        return latest.version + 1

    return 1


def get_opportunity_or_none(
    db: Session,
    opportunity_id: int,
):
    """
    Return an Opportunity if it exists.
    """

    return (
        db.query(Opportunity)
        .filter(
            Opportunity.id
            == opportunity_id
        )
        .first()
    )


def get_latest_proposal_for_opportunity(
    db: Session,
    opportunity_id: int,
):
    """
    Return the latest Proposal associated
    with an Opportunity.
    """

    return (
        db.query(Proposal)
        .filter(
            Proposal.opportunity_id
            == opportunity_id
        )
        .order_by(
            Proposal.version.desc(),
            Proposal.id.desc(),
        )
        .first()
    )


def proposal_exists_for_opportunity(
    db: Session,
    opportunity_id: int,
) -> bool:
    """
    Check whether an Opportunity already
    has at least one Proposal.

    Used to prevent accidental duplicate
    initial proposal generation.
    """

    existing = (
        db.query(Proposal.id)
        .filter(
            Proposal.opportunity_id
            == opportunity_id
        )
        .first()
    )

    return existing is not None
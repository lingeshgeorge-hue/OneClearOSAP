from datetime import datetime

from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.models.opportunity import Opportunity


def generate_proposal_number(
    db: Session,
) -> str:
    """
    Generate the next unique proposal number.

    Format:
    OCP-YYYY-0001
    OCP-YYYY-0002
    OCP-YYYY-0003

    Uses existing proposal numbers rather than row count,
    preventing duplicates if proposals have been deleted.
    """

    year = datetime.now().year

    prefix = f"OCP-{year}-"

    existing_proposals = (
        db.query(Proposal.proposal_number)
        .filter(
            Proposal.proposal_number.like(
                f"{prefix}%"
            )
        )
        .all()
    )

    highest_number = 0

    for proposal in existing_proposals:

        proposal_number = proposal[0]

        if not proposal_number:
            continue

        try:
            sequence = int(
                proposal_number.split("-")[-1]
            )

            if sequence > highest_number:
                highest_number = sequence

        except (ValueError, IndexError):
            continue

    next_number = highest_number + 1

    return (
        f"{prefix}"
        f"{next_number:04d}"
    )


def get_next_version(
    db: Session,
    opportunity_id: int,
) -> int:
    """
    Return the next proposal version
    for a specific opportunity.
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
    Return an Opportunity if it exists,
    otherwise return None.
    """

    return (
        db.query(Opportunity)
        .filter(
            Opportunity.id
            == opportunity_id
        )
        .first()
    )
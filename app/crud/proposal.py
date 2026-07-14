from sqlalchemy.orm import Session
from app.models.proposal import Proposal
from app.schemas.proposal import ProposalCreate


def create_proposal(
    db: Session,
    proposal: ProposalCreate
):
    try:
        db_proposal = Proposal(
            **proposal.model_dump()
        )

        db.add(db_proposal)
        db.commit()
        db.refresh(db_proposal)

        return db_proposal

    except Exception as e:
        db.rollback()
        print("PROPOSAL ERROR:", repr(e))
        raise e
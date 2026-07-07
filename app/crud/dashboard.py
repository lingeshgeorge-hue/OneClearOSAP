from sqlalchemy.orm import Session

from app.models.user import User
from app.models.clinic import Clinic
from app.models.lead import Lead


def get_dashboard(db: Session):

    return {
        "total_users": db.query(User).count(),

        "total_clinics": db.query(Clinic).count(),

        "total_leads": db.query(Lead).count(),

        "new_leads": db.query(Lead).filter(
            Lead.status == "New"
        ).count(),

        "qualified_leads": db.query(Lead).filter(
            Lead.status == "Qualified"
        ).count(),

        "won_leads": db.query(Lead).filter(
            Lead.status == "Won"
        ).count(),

        "lost_leads": db.query(Lead).filter(
            Lead.status == "Lost"
        ).count(),
    }
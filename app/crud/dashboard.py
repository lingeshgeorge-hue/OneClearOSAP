from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.lead import Lead


def get_dashboard_metrics(db: Session):

    total_leads = db.query(Lead).count()

    new_leads = db.query(Lead).filter(
        Lead.status == "New"
    ).count()

    contacted_leads = db.query(Lead).filter(
        Lead.status == "Contacted"
    ).count()

    qualified_leads = db.query(Lead).filter(
        Lead.status == "Qualified"
    ).count()

    high_priority_leads = db.query(Lead).filter(
        Lead.priority == "HIGH"
    ).count()

    followups_due_today = db.query(Lead).filter(
        Lead.next_followup.isnot(None),
        func.date(Lead.next_followup) <= date.today()
    ).count()

    assigned_leads = db.query(Lead).filter(
        Lead.assigned_to.isnot(None)
    ).count()

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "contacted_leads": contacted_leads,
        "qualified_leads": qualified_leads,
        "high_priority_leads": high_priority_leads,
        "followups_due_today": followups_due_today,
        "assigned_leads": assigned_leads
    }
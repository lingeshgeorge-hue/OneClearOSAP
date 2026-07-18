from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.lead import Lead
from app.models.contact import Contact
from app.models.opportunity import Opportunity
from app.models.proposal import Proposal
from app.models.client import Client


def get_dashboard_data(db: Session):
    total_leads = db.query(Lead).count()

    total_contacts = db.query(Contact).count()

    total_opportunities = db.query(
        Opportunity
    ).count()

    total_proposals = db.query(
        Proposal
    ).count()

    total_clients = db.query(
        Client
    ).count()

    pipeline_value = (
        db.query(
            func.sum(
                Opportunity.estimated_value
            )
        ).scalar() or 0
    )

    active_clients = (
        db.query(Client)
        .filter(
            Client.status == "Active"
        )
        .count()
    )

    onboarding_clients = (
        db.query(Client)
        .filter(
            Client.status == "Onboarding"
        )
        .count()
    )

    monthly_revenue = (
        db.query(
            func.sum(
                Client.monthly_revenue
            )
        ).scalar() or 0
    )

    return {
        "total_leads": total_leads,
        "total_contacts": total_contacts,
        "total_opportunities": total_opportunities,
        "total_proposals": total_proposals,
        "total_clients": total_clients,
        "pipeline_value": pipeline_value,
        "active_clients": active_clients,
        "onboarding_clients": onboarding_clients,
        "monthly_revenue": monthly_revenue
    }
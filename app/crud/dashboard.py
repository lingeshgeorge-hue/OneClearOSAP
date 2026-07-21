from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.contact import Contact
from app.models.opportunity import Opportunity
from app.models.proposal import Proposal
from app.models.client import Client


def get_dashboard_data(db: Session):
    """
    Return CRM dashboard analytics.

    Important:
    Proposal revisions are not counted as separate
    Opportunity -> Proposal conversions.
    """

    now = datetime.now()
    today = now.date()
    upcoming_limit = now + timedelta(days=7)

    # =========================================================
    # BASIC COUNTS
    # =========================================================

    total_leads = db.query(Lead).count()

    total_contacts = db.query(Contact).count()

    total_opportunities = (
        db.query(Opportunity).count()
    )

    total_proposals = (
        db.query(Proposal).count()
    )

    total_clients = (
        db.query(Client).count()
    )

    # Count unique opportunities that have proposals.
    # This prevents V1, V2, V3 revisions from inflating
    # proposal conversion analytics.
    opportunities_with_proposals = (
        db.query(
            func.count(
                func.distinct(
                    Proposal.opportunity_id
                )
            )
        )
        .scalar()
        or 0
    )

    # =========================================================
    # CLIENT COUNTS
    # =========================================================

    active_clients = (
        db.query(Client)
        .filter(
            func.upper(Client.status)
            == "ACTIVE"
        )
        .count()
    )

    onboarding_clients = (
        db.query(Client)
        .filter(
            func.upper(Client.status)
            == "ONBOARDING"
        )
        .count()
    )

    # =========================================================
    # PIPELINE VALUE
    # =========================================================

    total_pipeline_value = (
        db.query(
            func.sum(
                Opportunity.estimated_value
            )
        )
        .scalar()
        or 0
    )

    opportunities = (
        db.query(Opportunity).all()
    )

    weighted_pipeline_value = 0

    for opportunity in opportunities:

        estimated_value = (
            opportunity.estimated_value
            or 0
        )

        probability = (
            opportunity.probability
            or 0
        )

        weighted_pipeline_value += (
            estimated_value
            * probability
            / 100
        )

    # =========================================================
    # CONTRACTED REVENUE
    # =========================================================

    monthly_contracted_revenue = (
        db.query(
            func.sum(
                Client.monthly_revenue
            )
        )
        .filter(
            func.upper(Client.status)
            == "ACTIVE"
        )
        .scalar()
        or 0
    )

    annual_contracted_revenue = (
        monthly_contracted_revenue
        * 12
    )

    # =========================================================
    # LEAD STATUS DISTRIBUTION
    # =========================================================

    lead_status_rows = (
        db.query(
            Lead.status,
            func.count(Lead.id),
        )
        .group_by(
            Lead.status
        )
        .all()
    )

    lead_status = {
        str(status): count
        for status, count
        in lead_status_rows
    }

    # =========================================================
    # LEAD PRIORITY DISTRIBUTION
    # =========================================================

    lead_priority_rows = (
        db.query(
            Lead.priority,
            func.count(Lead.id),
        )
        .group_by(
            Lead.priority
        )
        .all()
    )

    lead_priority = {
        str(priority): count
        for priority, count
        in lead_priority_rows
    }

    # =========================================================
    # OPPORTUNITY STAGE DISTRIBUTION
    # =========================================================

    opportunity_stage_rows = (
        db.query(
            Opportunity.stage,
            func.count(Opportunity.id),
        )
        .group_by(
            Opportunity.stage
        )
        .all()
    )

    opportunity_stage = {
        str(stage): count
        for stage, count
        in opportunity_stage_rows
    }

    # =========================================================
    # PROPOSAL STATUS DISTRIBUTION
    # =========================================================

    proposal_status_rows = (
        db.query(
            Proposal.status,
            func.count(Proposal.id),
        )
        .group_by(
            Proposal.status
        )
        .all()
    )

    proposal_status = {
        str(status): count
        for status, count
        in proposal_status_rows
    }

    # =========================================================
    # CONVERSION RATES
    # =========================================================

    leads_with_opportunities = (
        db.query(
            func.count(
                func.distinct(
                    Opportunity.lead_id
                )
            )
        )
        .scalar()
        or 0
    )

    lead_to_opportunity_rate = (
        (
            leads_with_opportunities
            / total_leads
        )
        * 100
        if total_leads
        else 0
    )

    opportunity_to_proposal_rate = (
        (
            opportunities_with_proposals
            / total_opportunities
        )
        * 100
        if total_opportunities
        else 0
    )

    # Count unique proposals converted to clients.
    converted_proposals = (
        db.query(
            func.count(
                func.distinct(
                    Client.proposal_id
                )
            )
        )
        .scalar()
        or 0
    )

    proposal_to_client_rate = (
        (
            converted_proposals
            / opportunities_with_proposals
        )
        * 100
        if opportunities_with_proposals
        else 0
    )

    converted_leads = (
        db.query(
            func.count(
                func.distinct(
                    Client.lead_id
                )
            )
        )
        .scalar()
        or 0
    )

    lead_to_client_rate = (
        (
            converted_leads
            / total_leads
        )
        * 100
        if total_leads
        else 0
    )

    # =========================================================
    # FOLLOW-UP ANALYTICS
    # =========================================================

    overdue_followups = (
        db.query(Lead)
        .filter(
            Lead.next_followup.isnot(None),
            Lead.next_followup < now,
        )
        .count()
    )

    due_today_followups = (
        db.query(Lead)
        .filter(
            Lead.next_followup.isnot(None),
            func.date(
                Lead.next_followup
            )
            == str(today),
        )
        .count()
    )

    upcoming_followups = (
        db.query(Lead)
        .filter(
            Lead.next_followup.isnot(None),
            Lead.next_followup > now,
            Lead.next_followup
            <= upcoming_limit,
        )
        .count()
    )

    # =========================================================
    # RESPONSE
    # =========================================================

    return {

        "summary": {
            "total_leads": total_leads,
            "total_contacts": total_contacts,
            "total_opportunities": (
                total_opportunities
            ),
            "total_proposals": (
                total_proposals
            ),
            "total_clients": total_clients,
            "active_clients": active_clients,
            "onboarding_clients": (
                onboarding_clients
            ),
        },

        "pipeline": {
            "total_pipeline_value": round(
                total_pipeline_value,
                2,
            ),
            "weighted_pipeline_value": round(
                weighted_pipeline_value,
                2,
            ),
        },

        "revenue": {
            "monthly_contracted_revenue": round(
                monthly_contracted_revenue,
                2,
            ),
            "annual_contracted_revenue": round(
                annual_contracted_revenue,
                2,
            ),
        },

        "conversion": {
            "lead_to_opportunity_rate": round(
                lead_to_opportunity_rate,
                2,
            ),
            "opportunity_to_proposal_rate": round(
                opportunity_to_proposal_rate,
                2,
            ),
            "proposal_to_client_rate": round(
                proposal_to_client_rate,
                2,
            ),
            "lead_to_client_rate": round(
                lead_to_client_rate,
                2,
            ),
        },

        "lead_status": lead_status,

        "lead_priority": lead_priority,

        "opportunity_stage": (
            opportunity_stage
        ),

        "proposal_status": (
            proposal_status
        ),

        "followups": {
            "overdue": overdue_followups,
            "due_today": due_today_followups,
            "upcoming_7_days": (
                upcoming_followups
            ),
        },
    }
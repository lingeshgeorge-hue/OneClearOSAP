from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.lead import Lead

from app.schemas.activity import ActivityCreate


# ============================================================
# HELPERS
# ============================================================

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


# ============================================================
# CREATE ACTIVITY
# ============================================================

def create_activity(
    db: Session,
    lead_id: int,
    activity: ActivityCreate,
    user_id: int,
):
    db_activity = Activity(
        lead_id=lead_id,
        activity_type=(
            activity.activity_type.strip()
        ),
        description=(
            activity.description.strip()
        ),
        created_by=user_id,
    )

    try:
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)

        return db_activity

    except Exception:
        db.rollback()
        raise


# ============================================================
# LEAD ACTIVITY HISTORY
# ============================================================

def get_lead_activities(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Activity)
        .filter(
            Activity.lead_id == lead_id
        )
        .order_by(
            Activity.created_at.desc(),
            Activity.id.desc(),
        )
        .all()
    )


# ============================================================
# USER ACTIVITY HISTORY
# ============================================================

def get_user_activities(
    db: Session,
    user_id: int,
):
    return (
        db.query(Activity)
        .filter(
            Activity.created_by == user_id
        )
        .order_by(
            Activity.created_at.desc(),
            Activity.id.desc(),
        )
        .all()
    )


# ============================================================
# USER ACTIVITY SUMMARY
# ============================================================

def get_user_activity_summary(
    db: Session,
    user_id: int,
):
    rows = (
        db.query(
            Activity.activity_type,
            func.count(Activity.id),
        )
        .filter(
            Activity.created_by == user_id
        )
        .group_by(
            Activity.activity_type
        )
        .all()
    )

    summary = {
        "total": 0,
        "calls": 0,
        "emails": 0,
        "meetings": 0,
        "follow_ups": 0,
        "other": 0,
    }

    for activity_type, count in rows:

        normalized = (
            activity_type
            or ""
        ).strip().lower()

        summary["total"] += count

        if normalized in {
            "call",
            "phone call",
            "outbound call",
            "inbound call",
        }:
            summary["calls"] += count

        elif normalized in {
            "email",
            "e-mail",
        }:
            summary["emails"] += count

        elif normalized in {
            "meeting",
            "demo",
            "presentation",
        }:
            summary["meetings"] += count

        elif normalized in {
            "follow-up",
            "follow up",
            "followup",
        }:
            summary["follow_ups"] += count

        else:
            summary["other"] += count

    return summary

from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate


def create_activity(
    db: Session,
    lead_id: int,
    activity: ActivityCreate,
    user_id: int
):
    db_activity = Activity(
        lead_id=lead_id,
        activity_type=activity.activity_type,
        description=activity.description,
        created_by=user_id
    )

    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    return db_activity


def get_lead_activities(
    db: Session,
    lead_id: int
):
    return (
        db.query(Activity)
        .filter(Activity.lead_id == lead_id)
        .order_by(Activity.created_at.desc())
        .all()
    )
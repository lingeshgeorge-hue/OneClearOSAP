from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.lead import Lead
from app.models.contact import Contact
from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)


# ============================================================
# HELPERS
# ============================================================

def _get_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def _get_lead(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Lead)
        .filter(Lead.id == lead_id)
        .first()
    )


def _get_contact(
    db: Session,
    contact_id: int,
):
    return (
        db.query(Contact)
        .filter(Contact.id == contact_id)
        .first()
    )


def _apply_completion_state(
    db_task: Task,
):
    """
    Keep completed_at synchronized with task status.
    """

    status_value = (
        db_task.status.strip().lower()
        if db_task.status
        else ""
    )

    if status_value == "completed":

        if db_task.completed_at is None:
            db_task.completed_at = datetime.utcnow()

    else:

        db_task.completed_at = None


# ============================================================
# CREATE TASK
# ============================================================

def create_task(
    db: Session,
    task: TaskCreate,
    user_id: int,
):
    """
    Create a new task.

    If assigned_to is not supplied,
    assign the task to the creator.
    """

    lead = _get_lead(
        db,
        task.lead_id,
    )

    if not lead:
        return None, "Lead not found"

    if task.contact_id is not None:

        contact = _get_contact(
            db,
            task.contact_id,
        )

        if not contact:
            return None, "Contact not found"

        if contact.lead_id != task.lead_id:
            return (
                None,
                "Contact does not belong to this lead",
            )

    assigned_user_id = (
        task.assigned_to
        if task.assigned_to is not None
        else user_id
    )

    assigned_user = _get_user(
        db,
        assigned_user_id,
    )

    if not assigned_user:
        return None, "Assigned user not found"

    task_data = task.model_dump()

    task_data["assigned_to"] = (
        assigned_user_id
    )

    db_task = Task(
        **task_data
    )

    _apply_completion_state(
        db_task
    )

    try:

        db.add(db_task)

        db.commit()

        db.refresh(db_task)

        return db_task, None

    except Exception:

        db.rollback()

        raise


# ============================================================
# GET TASKS
# ============================================================

def get_all_tasks(
    db: Session,
):
    return (
        db.query(Task)
        .order_by(
            Task.created_at.desc()
        )
        .all()
    )


def get_tasks_by_assignee(
    db: Session,
    user_id: int,
):
    return (
        db.query(Task)
        .filter(
            Task.assigned_to == user_id
        )
        .order_by(
            Task.due_date.asc(),
            Task.created_at.desc(),
        )
        .all()
    )


def get_task_by_id(
    db: Session,
    task_id: int,
):
    return (
        db.query(Task)
        .filter(
            Task.id == task_id
        )
        .first()
    )


# ============================================================
# TASK FILTERS
# ============================================================

def get_overdue_tasks(
    db: Session,
    user_id: int | None = None,
):
    now = datetime.utcnow()

    query = (
        db.query(Task)
        .filter(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "Completed",
        )
    )

    if user_id is not None:
        query = query.filter(
            Task.assigned_to == user_id
        )

    return (
        query
        .order_by(Task.due_date.asc())
        .all()
    )


def get_tasks_due_today(
    db: Session,
    user_id: int | None = None,
):
    now = datetime.utcnow()

    start_of_day = datetime(
        now.year,
        now.month,
        now.day,
    )

    end_of_day = (
        start_of_day
        + timedelta(days=1)
    )

    query = (
        db.query(Task)
        .filter(
            Task.due_date.isnot(None),
            Task.due_date >= start_of_day,
            Task.due_date < end_of_day,
            Task.status != "Completed",
        )
    )

    if user_id is not None:
        query = query.filter(
            Task.assigned_to == user_id
        )

    return (
        query
        .order_by(Task.due_date.asc())
        .all()
    )


def get_upcoming_tasks(
    db: Session,
    user_id: int | None = None,
    days: int = 7,
):
    now = datetime.utcnow()

    end_date = (
        now
        + timedelta(days=days)
    )

    query = (
        db.query(Task)
        .filter(
            Task.due_date.isnot(None),
            Task.due_date > now,
            Task.due_date <= end_date,
            Task.status != "Completed",
        )
    )

    if user_id is not None:
        query = query.filter(
            Task.assigned_to == user_id
        )

    return (
        query
        .order_by(Task.due_date.asc())
        .all()
    )


# ============================================================
# UPDATE TASK
# ============================================================

def update_task(
    db: Session,
    task_id: int,
    task: TaskUpdate,
):
    db_task = get_task_by_id(
        db,
        task_id,
    )

    if not db_task:
        return None, "Task not found"

    update_data = task.model_dump(
        exclude_unset=True
    )

    final_lead_id = update_data.get(
        "lead_id",
        db_task.lead_id,
    )

    lead = _get_lead(
        db,
        final_lead_id,
    )

    if not lead:
        return None, "Lead not found"

    final_contact_id = update_data.get(
        "contact_id",
        db_task.contact_id,
    )

    if final_contact_id is not None:

        contact = _get_contact(
            db,
            final_contact_id,
        )

        if not contact:
            return None, "Contact not found"

        if contact.lead_id != final_lead_id:
            return (
                None,
                "Contact does not belong to this lead",
            )

    if (
        "assigned_to" in update_data
        and update_data["assigned_to"]
        is not None
    ):

        assigned_user = _get_user(
            db,
            update_data["assigned_to"],
        )

        if not assigned_user:
            return (
                None,
                "Assigned user not found",
            )

    for key, value in update_data.items():

        setattr(
            db_task,
            key,
            value,
        )

    _apply_completion_state(
        db_task
    )

    try:

        db.commit()

        db.refresh(db_task)

        return db_task, None

    except Exception:

        db.rollback()

        raise


# ============================================================
# DELETE TASK
# ============================================================

def delete_task(
    db: Session,
    task_id: int,
):
    db_task = get_task_by_id(
        db,
        task_id,
    )

    if not db_task:
        return None

    try:

        db.delete(db_task)

        db.commit()

        return db_task

    except Exception:

        db.rollback()

        raise
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.lead import Lead
from app.models.contact import Contact

from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task: TaskCreate):
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == task.lead_id).first()

    if not lead:
        return None, "Lead not found"

    # Verify contact if provided
    if task.contact_id is not None:
        contact = (
            db.query(Contact)
            .filter(Contact.id == task.contact_id)
            .first()
        )

        if not contact:
            return None, "Contact not found"

        if contact.lead_id != task.lead_id:
            return None, "Contact does not belong to this lead"

    db_task = Task(**task.model_dump())

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task, None


def get_all_tasks(db: Session):
    return db.query(Task).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(
    db: Session,
    task_id: int,
    task: TaskUpdate,
):
    db_task = get_task_by_id(db, task_id)

    if not db_task:
        return None

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return db_task


def delete_task(
    db: Session,
    task_id: int,
):
    db_task = get_task_by_id(db, task_id)

    if not db_task:
        return None

    db.delete(db_task)
    db.commit()

    return db_task
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from app.crud.task import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
)

from app.models.user import User
from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "/",
    response_model=TaskResponse
)
def create_new_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.SALES,
        ])
    ),
):
    new_task, error = create_task(db, task)

    if error:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return new_task


@router.get(
    "/",
    response_model=list[TaskResponse]
)
def read_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def edit_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.SALES,
        ])
    ),
):
    updated = update_task(
        db,
        task_id,
        task,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return updated


@router.delete(
    "/{task_id}"
)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
        ])
    ),
):
    deleted = delete_task(
        db,
        task_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {
        "message": "Task deleted successfully"
    }
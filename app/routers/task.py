from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

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
    get_tasks_by_assignee,
    get_task_by_id,
    get_overdue_tasks,
    get_tasks_due_today,
    get_upcoming_tasks,
    update_task,
    delete_task,
)

from app.models.user import User

from app.core.security import get_current_user
from app.core.permissions import RoleChecker
from app.core.roles import Roles


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ============================================================
# CREATE TASK
# Admin / Manager
# ============================================================

@router.post(
    "/",
    response_model=TaskResponse,
)
def create_new_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        RoleChecker([
            Roles.ADMIN,
            Roles.MANAGER,
        ])
    ),
):
    new_task, error = create_task(
        db,
        task,
        current_user.id,
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return new_task


# ============================================================
# GET TASKS
# Admin / Manager -> all
# Other authenticated users -> assigned tasks only
# ============================================================

@router.get(
    "/",
    response_model=list[TaskResponse],
)
def read_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_all_tasks(db)

    return get_tasks_by_assignee(
        db,
        current_user.id,
    )


# ============================================================
# MY TASKS
# ============================================================

@router.get(
    "/my",
    response_model=list[TaskResponse],
)
def read_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_tasks_by_assignee(
        db,
        current_user.id,
    )


# ============================================================
# OVERDUE TASKS
# Admin / Manager -> all
# Other users -> own tasks
# ============================================================

@router.get(
    "/overdue",
    response_model=list[TaskResponse],
)
def read_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_overdue_tasks(db)

    return get_overdue_tasks(
        db,
        current_user.id,
    )


# ============================================================
# TASKS DUE TODAY
# ============================================================

@router.get(
    "/due-today",
    response_model=list[TaskResponse],
)
def read_tasks_due_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_tasks_due_today(db)

    return get_tasks_due_today(
        db,
        current_user.id,
    )


# ============================================================
# UPCOMING TASKS - NEXT 7 DAYS
# ============================================================

@router.get(
    "/upcoming",
    response_model=list[TaskResponse],
)
def read_upcoming_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:
        return get_upcoming_tasks(
            db,
            days=7,
        )

    return get_upcoming_tasks(
        db,
        current_user.id,
        days=7,
    )


# ============================================================
# GET ONE TASK
# Keep dynamic route after static routes above.
# ============================================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    task = get_task_by_id(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Admin and Manager can view any task.
    # Other users can view only tasks assigned to them.
    if (
        current_user.role
        not in [
            Roles.ADMIN,
            Roles.MANAGER,
        ]
        and task.assigned_to
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access this task"
            ),
        )

    return task


# ============================================================
# UPDATE TASK
#
# Admin / Manager:
#   - Can fully update any task.
#
# Sales / Other authenticated users:
#   - Can update only their own assigned task.
#   - Can change status only.
# ============================================================

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def edit_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # --------------------------------------------------------
    # 1. Verify task exists
    # --------------------------------------------------------

    existing_task = get_task_by_id(
        db,
        task_id,
    )

    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # --------------------------------------------------------
    # 2. Admin / Manager can fully update any task
    # --------------------------------------------------------

    if current_user.role in [
        Roles.ADMIN,
        Roles.MANAGER,
    ]:

        updated, error = update_task(
            db,
            task_id,
            task,
        )

        if error:

            if error == "Task not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error,
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        return updated

    # --------------------------------------------------------
    # 3. Other users may update only their assigned task
    # --------------------------------------------------------

    if (
        existing_task.assigned_to
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this task"
            ),
        )

    # --------------------------------------------------------
    # 4. Sales / other users may change status only
    # --------------------------------------------------------

    update_data = task.model_dump(
        exclude_unset=True
    )

    disallowed_fields = (
        set(update_data.keys())
        - {"status"}
    )

    if disallowed_fields:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You may only update the status "
                "of your assigned task"
            ),
        )

    if "status" not in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No status update provided",
        )

    # --------------------------------------------------------
    # 5. Apply status update
    #
    # update_task() automatically manages completed_at:
    # Completed -> timestamp added
    # Reopened  -> completed_at cleared
    # --------------------------------------------------------

    updated, error = update_task(
        db,
        task_id,
        task,
    )

    if error:

        if error == "Task not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return updated

# ============================================================
# DELETE TASK
# Admin only
# ============================================================

@router.delete(
    "/{task_id}",
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return {
        "message": (
            "Task deleted successfully"
        )
    }

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    lead_id: int
    contact_id: Optional[int] = None

    title: str
    description: Optional[str] = None

    due_date: Optional[datetime] = None

    priority: Optional[str] = "Medium"

    status: Optional[str] = "Pending"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    contact_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
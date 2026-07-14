from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ActivityCreate(BaseModel):
    activity_type: str
    description: str


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    activity_type: str
    description: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
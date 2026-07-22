from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ActivityCreate(BaseModel):
    activity_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


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


class ActivitySummary(BaseModel):
    total: int
    calls: int
    emails: int
    meetings: int
    follow_ups: int
    other: int

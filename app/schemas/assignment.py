from pydantic import BaseModel


class AssignRequest(BaseModel):
    user_id: int
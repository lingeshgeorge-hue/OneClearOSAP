from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    manager_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


class ManagerAssignmentRequest(BaseModel):
    manager_id: Optional[int] = None

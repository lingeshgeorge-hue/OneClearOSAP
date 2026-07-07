from pydantic import BaseModel


class ClinicCreate(BaseModel):
    clinic_name: str
    phone: str
    email: str
    website: str
    city: str
    state: str
    specialty: str


class ClinicResponse(ClinicCreate):
    id: int

    class Config:
        from_attributes = True
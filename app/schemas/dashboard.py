from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_users: int

    total_clinics: int

    total_leads: int

    new_leads: int

    qualified_leads: int

    won_leads: int

    lost_leads: int
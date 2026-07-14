from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    high_priority_leads: int
    followups_due_today: int
    assigned_leads: int
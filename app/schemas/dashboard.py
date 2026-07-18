from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_leads: int
    total_contacts: int
    total_opportunities: int
    total_proposals: int
    total_clients: int

    pipeline_value: float
    active_clients: int
    onboarding_clients: int
    monthly_revenue: float
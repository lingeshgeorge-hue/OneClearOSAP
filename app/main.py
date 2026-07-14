from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

from app.models.user import User
from app.models.clinic import Clinic
from app.models.lead import Lead
from app.models.contact import Contact
from app.models.task import Task

from app.routers.user import router as user_router
from app.routers.clinic import router as clinic_router
from app.routers.lead import router as lead_router
from app.routers.dashboard import router as dashboard_router
from app.routers.contact import router as contact_router
from app.routers.task import router as task_router
from app.routers.activity import router as activity_router
from app.routers import opportunity
from app.models.opportunity import Opportunity
from app.models.proposal import Proposal
from app.routers import proposal

app = FastAPI(
    title="OneClear OSAP",
    description="AI Powered Sales Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Welcome to OneClear OSAP!",
        "company": "OneClearRCM",
        "status": "Running Successfully"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }


app.include_router(clinic_router)
app.include_router(user_router)
app.include_router(lead_router)
app.include_router(dashboard_router)
app.include_router(contact_router)
app.include_router(task_router)
app.include_router(activity_router)
app.include_router(opportunity.router)
app.include_router(proposal.router)
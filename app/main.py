from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.audit import router as audit_router
from app.api.v1.claim_detail import router as claim_detail_router
from app.api.v1.claims import router as claims_router
from app.api.v1.documents import router as documents_router
from app.api.v1.extractions import router as extractions_router
from app.api.v1.health import router as health_router
from app.api.v1.summaries import router as summaries_router
from app.api.v1.triage import router as triage_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
from app.db.models import Claim, AuditLog, Document, Extraction, ClaimSummary, TriageResult  # noqa: F401

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.6.0",
    description="Explainable AI Claims Triage & Document Intelligence Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(extractions_router)
app.include_router(summaries_router)
app.include_router(triage_router)
app.include_router(audit_router)
app.include_router(claim_detail_router)
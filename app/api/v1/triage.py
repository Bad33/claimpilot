from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.db.models.triage_result import TriageResult
from app.schemas.triage import TriageResultResponse
from app.services.audit_service import AuditService
from app.services.triage_service import TriageService

router = APIRouter(prefix="/api/v1/claims", tags=["triage"])


@router.post(
    "/{claim_id}/triage",
    response_model=TriageResultResponse,
    status_code=status.HTTP_200_OK,
)
def run_triage(claim_id: int, db: Session = Depends(get_db)) -> TriageResult:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    documents = (
        db.query(Document)
        .filter(Document.claim_id == claim_id)
        .order_by(Document.created_at.asc())
        .all()
    )
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for this claim.",
        )

    extractions = (
        db.query(Extraction)
        .filter(Extraction.claim_id == claim_id)
        .order_by(Extraction.created_at.asc())
        .all()
    )
    if not extractions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extractions found for this claim. Run extraction first.",
        )

    result = TriageService.run_triage(
        db=db,
        claim=claim,
        documents=documents,
        extractions=extractions,
    )

    AuditService.log_event(
        db=db,
        event_type="claim_triage_completed",
        actor="api",
        claim_id=claim_id,
        event_payload={
            "complexity_label": result.complexity_label,
            "complexity_score": result.complexity_score,
            "routing_label": result.routing_label,
            "routing_confidence": result.routing_confidence,
            "requires_human_review": result.requires_human_review,
            "reason_codes": result.reason_codes,
            "review_flags": result.review_flags,
            "model_version": result.model_version,
        },
    )

    return result


@router.get(
    "/{claim_id}/triage",
    response_model=TriageResultResponse,
    status_code=status.HTTP_200_OK,
)
def get_triage(claim_id: int, db: Session = Depends(get_db)) -> TriageResult:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    triage = db.query(TriageResult).filter(TriageResult.claim_id == claim_id).first()
    if not triage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No triage result found for this claim. Run triage first.",
        )

    return triage
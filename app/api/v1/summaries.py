from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.db.models.claim_summary import ClaimSummary
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.schemas.summary import ClaimSummaryResponse
from app.services.audit_service import AuditService
from app.services.summarization_service import SummarizationService

router = APIRouter(prefix="/api/v1/claims", tags=["summaries"])


@router.post(
    "/{claim_id}/summarize",
    response_model=ClaimSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def summarize_claim(claim_id: int, db: Session = Depends(get_db)) -> ClaimSummary:
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
            detail="No documents found for this claim. Upload a document first.",
        )

    extractions = (
        db.query(Extraction)
        .filter(Extraction.claim_id == claim_id)
        .order_by(Extraction.created_at.asc())
        .all()
    )

    result = SummarizationService.generate_summary(
        claim=claim,
        documents=documents,
        extractions=extractions,
    )

    summary = SummarizationService.save_summary(
        db=db,
        claim_id=claim_id,
        summary_text=result.summary_text,
        model_name=result.model_name,
        confidence=result.confidence,
        source_snippets=result.source_snippets,
    )

    AuditService.log_event(
        db=db,
        event_type="claim_summary_generated",
        actor="api",
        claim_id=claim_id,
        event_payload={
            "summary_id": summary.id,
            "model_name": summary.model_name,
            "confidence": summary.confidence,
            "source_snippet_count": len(summary.source_snippets or []),
        },
    )

    return summary


@router.get(
    "/{claim_id}/summary",
    response_model=ClaimSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_claim_summary(claim_id: int, db: Session = Depends(get_db)) -> ClaimSummary:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    summary = db.query(ClaimSummary).filter(ClaimSummary.claim_id == claim_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No summary found for this claim. Run summarization first.",
        )

    return summary
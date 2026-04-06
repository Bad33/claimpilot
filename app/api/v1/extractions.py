from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.schemas.extraction import ExtractionResponse, ExtractionRunResponse
from app.services.audit_service import AuditService
from app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/api/v1/claims", tags=["extractions"])


@router.post(
    "/{claim_id}/extract",
    response_model=ExtractionRunResponse,
    status_code=status.HTTP_200_OK,
)
def run_extraction(claim_id: int, db: Session = Depends(get_db)) -> ExtractionRunResponse:
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

    saved_extractions = ExtractionService.save_extractions_for_claim(
        db=db,
        claim_id=claim_id,
        documents=documents,
    )

    AuditService.log_event(
        db=db,
        event_type="claim_extraction_completed",
        actor="api",
        claim_id=claim_id,
        event_payload={
            "total_extractions": len(saved_extractions),
            "fields": [item.field_name for item in saved_extractions],
        },
    )

    return ExtractionRunResponse(
        claim_id=claim_id,
        total_extractions=len(saved_extractions),
        extracted_fields=saved_extractions,
    )


@router.get(
    "/{claim_id}/extractions",
    response_model=list[ExtractionResponse],
    status_code=status.HTTP_200_OK,
)
def list_extractions(claim_id: int, db: Session = Depends(get_db)) -> list[Extraction]:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    extractions = (
        db.query(Extraction)
        .filter(Extraction.claim_id == claim_id)
        .order_by(Extraction.created_at.desc())
        .all()
    )
    return extractions
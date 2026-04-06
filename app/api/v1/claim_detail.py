from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.db.models.claim_summary import ClaimSummary
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.db.models.triage_result import TriageResult
from app.schemas.claim_detail import ClaimDetailResponse

router = APIRouter(prefix="/api/v1/claims", tags=["claim-detail"])


@router.get(
    "/{claim_id}/full",
    response_model=ClaimDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_full_claim(claim_id: int, db: Session = Depends(get_db)) -> ClaimDetailResponse:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    documents = (
        db.query(Document)
        .filter(Document.claim_id == claim_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    extractions = (
        db.query(Extraction)
        .filter(Extraction.claim_id == claim_id)
        .order_by(Extraction.created_at.desc())
        .all()
    )
    summary = db.query(ClaimSummary).filter(ClaimSummary.claim_id == claim_id).first()
    triage = db.query(TriageResult).filter(TriageResult.claim_id == claim_id).first()

    return ClaimDetailResponse(
        claim=claim,
        documents=documents,
        extractions=extractions,
        summary=summary,
        triage=triage,
    )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.schemas.claim import ClaimCreate, ClaimResponse

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def create_claim(payload: ClaimCreate, db: Session = Depends(get_db)) -> Claim:
    existing_claim = (
        db.query(Claim)
        .filter(Claim.external_claim_id == payload.external_claim_id)
        .first()
    )
    if existing_claim:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Claim with external_claim_id '{payload.external_claim_id}' already exists.",
        )

    claim = Claim(
        external_claim_id=payload.external_claim_id,
        claimant_name=payload.claimant_name,
        incident_date=payload.incident_date,
        claim_type=payload.claim_type,
        claimed_amount=payload.claimed_amount,
        status=payload.status,
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: int, db: Session = Depends(get_db)) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )
    return claim
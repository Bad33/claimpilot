from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.audit_log import AuditLog
from app.db.models.claim import Claim
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/api/v1/claims", tags=["audit"])


@router.get(
    "/{claim_id}/audit",
    response_model=list[AuditLogResponse],
    status_code=status.HTTP_200_OK,
)
def get_claim_audit(claim_id: int, db: Session = Depends(get_db)) -> list[AuditLog]:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.claim_id == claim_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return logs
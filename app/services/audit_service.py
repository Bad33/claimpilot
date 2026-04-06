from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        actor: str = "system",
        claim_id: int | None = None,
        event_payload: dict | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            claim_id=claim_id,
            event_type=event_type,
            actor=actor,
            event_payload=event_payload,
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
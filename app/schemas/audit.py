from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int | None
    event_type: str
    actor: str
    event_payload: dict | None
    created_at: datetime
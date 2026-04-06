from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TriageResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    complexity_label: str
    complexity_score: float
    routing_label: str
    routing_confidence: float
    requires_human_review: bool
    reason_codes: list[str] | None
    review_flags: list[str] | None
    feature_snapshot: dict | None
    model_version: str
    created_at: datetime
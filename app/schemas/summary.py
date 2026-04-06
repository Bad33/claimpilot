from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClaimSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    summary_text: str
    model_name: str
    confidence: float
    source_snippets: list[str] | None
    created_at: datetime
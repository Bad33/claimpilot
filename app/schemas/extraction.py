from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    document_id: int
    field_name: str
    field_value: str
    confidence: float
    extraction_method: str
    source_snippet: str | None
    created_at: datetime


class ExtractionRunResponse(BaseModel):
    claim_id: int
    total_extractions: int
    extracted_fields: list[ExtractionResponse]
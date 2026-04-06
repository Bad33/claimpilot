from pydantic import BaseModel

from app.schemas.claim import ClaimResponse
from app.schemas.document import DocumentResponse
from app.schemas.extraction import ExtractionResponse
from app.schemas.summary import ClaimSummaryResponse
from app.schemas.triage import TriageResultResponse


class ClaimDetailResponse(BaseModel):
    claim: ClaimResponse
    documents: list[DocumentResponse]
    extractions: list[ExtractionResponse]
    summary: ClaimSummaryResponse | None
    triage: TriageResultResponse | None
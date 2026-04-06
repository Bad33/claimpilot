from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClaimCreate(BaseModel):
    external_claim_id: str = Field(..., min_length=3, max_length=100)
    claimant_name: str = Field(..., min_length=2, max_length=255)
    incident_date: Optional[date] = None
    claim_type: str = Field(..., min_length=2, max_length=100)
    claimed_amount: Optional[Decimal] = Field(default=None, ge=0)
    status: str = Field(default="new", min_length=2, max_length=50)


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_claim_id: str
    claimant_name: str
    incident_date: Optional[date]
    claim_type: str
    claimed_amount: Optional[Decimal]
    status: str
    created_at: datetime
    updated_at: datetime
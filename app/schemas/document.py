from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    filename: str
    file_type: str
    content_type: str
    file_size: int
    parse_status: str
    parsed_text: Optional[str]
    created_at: datetime
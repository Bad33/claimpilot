import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.utils.evidence import extract_evidence_snippet
from app.utils.regex_patterns import (
    CLAIM_AMOUNT_PATTERNS,
    CLAIM_NUMBER_PATTERNS,
    CLAIM_TYPE_PATTERNS,
    CLAIMANT_NAME_PATTERNS,
    INCIDENT_DATE_PATTERNS,
)


@dataclass
class ExtractedFieldResult:
    field_name: str
    field_value: str
    confidence: float
    extraction_method: str
    source_snippet: str | None


class ExtractionService:
    FIELD_CONFIG = {
        "claim_number": {
            "patterns": CLAIM_NUMBER_PATTERNS,
            "confidence": 0.98,
        },
        "claimant_name": {
            "patterns": CLAIMANT_NAME_PATTERNS,
            "confidence": 0.92,
        },
        "incident_date": {
            "patterns": INCIDENT_DATE_PATTERNS,
            "confidence": 0.96,
        },
        "claim_type": {
            "patterns": CLAIM_TYPE_PATTERNS,
            "confidence": 0.90,
        },
        "claimed_amount": {
            "patterns": CLAIM_AMOUNT_PATTERNS,
            "confidence": 0.97,
        },
    }

    @classmethod
    def _extract_single_field(cls, text: str, field_name: str) -> ExtractedFieldResult | None:
        config = cls.FIELD_CONFIG[field_name]

        for pattern in config["patterns"]:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                value = match.group(1).strip()

                # Basic cleanup
                if field_name == "claimed_amount":
                    value = value.replace(",", "")
                if field_name in {"claim_type", "claimant_name"}:
                    value = re.sub(r"\s+", " ", value)

                snippet = extract_evidence_snippet(text, value)

                return ExtractedFieldResult(
                    field_name=field_name,
                    field_value=value,
                    confidence=config["confidence"],
                    extraction_method="regex",
                    source_snippet=snippet,
                )

        return None

    @classmethod
    def extract_from_document(cls, text: str) -> list[ExtractedFieldResult]:
        results: list[ExtractedFieldResult] = []

        for field_name in cls.FIELD_CONFIG:
            result = cls._extract_single_field(text, field_name)
            if result:
                results.append(result)

        return results

    @classmethod
    def save_extractions_for_claim(cls, db: Session, claim_id: int, documents: list[Document]) -> list[Extraction]:
        saved_extractions: list[Extraction] = []

        # Optional cleanup: remove old extractions before rerun
        db.query(Extraction).filter(Extraction.claim_id == claim_id).delete()
        db.commit()

        for document in documents:
            if not document.parsed_text:
                continue

            extracted_fields = cls.extract_from_document(document.parsed_text)

            for item in extracted_fields:
                extraction = Extraction(
                    claim_id=claim_id,
                    document_id=document.id,
                    field_name=item.field_name,
                    field_value=item.field_value,
                    confidence=item.confidence,
                    extraction_method=item.extraction_method,
                    source_snippet=item.source_snippet,
                )
                db.add(extraction)
                saved_extractions.append(extraction)

        db.commit()

        for extraction in saved_extractions:
            db.refresh(extraction)

        return saved_extractions
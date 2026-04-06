from decimal import Decimal

from app.db.models.claim import Claim
from app.db.models.document import Document
from app.db.models.extraction import Extraction


class FeatureService:
    @staticmethod
    def _joined_text(documents: list[Document]) -> str:
        return " ".join([doc.parsed_text or "" for doc in documents]).lower()

    @staticmethod
    def _missing_field_count(extractions: list[Extraction]) -> int:
        required = {"claim_number", "claimant_name", "incident_date", "claim_type", "claimed_amount"}
        found = {e.field_name for e in extractions}
        return len(required - found)

    @staticmethod
    def _claim_type_flags(claim: Claim, extractions: list[Extraction]) -> tuple[int, int]:
        extracted_type = None
        for e in extractions:
            if e.field_name == "claim_type":
                extracted_type = e.field_value.lower()
                break

        claim_type = (extracted_type or claim.claim_type or "").lower()
        is_auto = 1 if "auto" in claim_type or "collision" in claim_type else 0
        is_property = 1 if "property" in claim_type or "fire" in claim_type or "water" in claim_type else 0
        return is_auto, is_property

    @staticmethod
    def build_features(claim: Claim, documents: list[Document], extractions: list[Extraction]) -> dict:
        text = FeatureService._joined_text(documents)
        auto_flag, property_flag = FeatureService._claim_type_flags(claim, extractions)

        amount = float(claim.claimed_amount or Decimal("0"))
        doc_count = len(documents)
        text_length = len(text)
        missing_fields = FeatureService._missing_field_count(extractions)

        features = {
            "amount": amount,
            "claim_type_auto": auto_flag,
            "claim_type_property": property_flag,
            "doc_count": doc_count,
            "text_length": text_length,
            "missing_fields": missing_fields,
            "has_police": 1 if "police report" in text or "police" in text else 0,
            "has_fire": 1 if "fire department" in text or "fire" in text else 0,
            "has_injury": 1 if "injury" in text or "injured" in text or "medical" in text else 0,
            "has_legal": 1 if "legal" in text or "attorney" in text or "lawyer" in text else 0,
            "has_pending": 1 if "pending" in text or "awaiting" in text else 0,
        }
        return features
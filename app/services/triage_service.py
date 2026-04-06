from sqlalchemy.orm import Session

from app.db.models.claim import Claim
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.db.models.triage_result import TriageResult
from app.services.complexity_model_service import ComplexityModelService
from app.services.feature_service import FeatureService
from app.services.routing_service import RoutingService


class TriageService:
    @staticmethod
    def run_triage(
        db: Session,
        claim: Claim,
        documents: list[Document],
        extractions: list[Extraction],
    ) -> TriageResult:
        features = FeatureService.build_features(claim, documents, extractions)
        prediction = ComplexityModelService.predict(features)
        routing = RoutingService.recommend_route(
            features=features,
            complexity_label=prediction["complexity_label"],
            complexity_score=prediction["complexity_score"],
        )

        existing = db.query(TriageResult).filter(TriageResult.claim_id == claim.id).first()

        if existing:
            existing.complexity_label = prediction["complexity_label"]
            existing.complexity_score = prediction["complexity_score"]
            existing.routing_label = routing["routing_label"]
            existing.routing_confidence = routing["routing_confidence"]
            existing.requires_human_review = routing["requires_human_review"]
            existing.reason_codes = routing["reason_codes"]
            existing.review_flags = routing["review_flags"]
            existing.feature_snapshot = features
            existing.model_version = prediction["model_version"]
            db.commit()
            db.refresh(existing)
            return existing

        result = TriageResult(
            claim_id=claim.id,
            complexity_label=prediction["complexity_label"],
            complexity_score=prediction["complexity_score"],
            routing_label=routing["routing_label"],
            routing_confidence=routing["routing_confidence"],
            requires_human_review=routing["requires_human_review"],
            reason_codes=routing["reason_codes"],
            review_flags=routing["review_flags"],
            feature_snapshot=features,
            model_version=prediction["model_version"],
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
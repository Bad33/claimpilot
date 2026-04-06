class RoutingService:
    @staticmethod
    def recommend_route(features: dict, complexity_label: str, complexity_score: float) -> dict:
        reason_codes: list[str] = []
        review_flags: list[str] = []
        routing_confidence = max(0.55, complexity_score)

        hard_escalation = False

        if features["amount"] >= 25000:
            reason_codes.append("HIGH_AMOUNT_THRESHOLD")
            hard_escalation = True

        if features["has_injury"]:
            reason_codes.append("INJURY_MENTIONED")
            hard_escalation = True

        if features["has_legal"]:
            reason_codes.append("LEGAL_OR_ATTORNEY_MENTIONED")
            hard_escalation = True

        if features["has_fire"]:
            reason_codes.append("FIRE_RELATED_LOSS")
            hard_escalation = True

        if features["has_police"]:
            reason_codes.append("POLICE_REPORT_REFERENCED")

        if features["has_pending"]:
            reason_codes.append("PENDING_DOCUMENTATION")

        if features["missing_fields"] >= 2:
            reason_codes.append("MISSING_CRITICAL_FIELDS")
            review_flags.append("LOW_STRUCTURED_COMPLETENESS")
            routing_confidence -= 0.15

        if features["doc_count"] <= 1:
            review_flags.append("LIMITED_DOCUMENT_CONTEXT")
            routing_confidence -= 0.05

        if features["text_length"] < 500:
            review_flags.append("SPARSE_TEXT_CONTEXT")
            routing_confidence -= 0.05

        if hard_escalation and complexity_label == "low":
            review_flags.append("RULE_MODEL_DISAGREEMENT")
            routing_confidence -= 0.10

        if hard_escalation:
            routing_label = "escalate"
            routing_confidence = max(0.75, routing_confidence)
        elif complexity_label == "high":
            reason_codes.append("MODEL_PREDICTED_HIGH_COMPLEXITY")
            routing_label = "escalate"
            routing_confidence = max(0.72, routing_confidence)
        elif complexity_label == "medium" or features["missing_fields"] > 0:
            reason_codes.append("MODEL_PREDICTED_MEDIUM_COMPLEXITY")
            routing_label = "adjuster_review"
            routing_confidence = max(0.65, routing_confidence)
        else:
            reason_codes.append("LOW_COMPLEXITY_AND_COMPLETE_DOCUMENTS")
            routing_label = "low_touch"
            routing_confidence = max(0.60, routing_confidence)

        routing_confidence = max(0.35, min(0.99, routing_confidence))

        return {
            "routing_label": routing_label,
            "routing_confidence": routing_confidence,
            "reason_codes": reason_codes,
            "review_flags": review_flags,
            "requires_human_review": routing_label != "low_touch" or len(review_flags) > 0,
        }
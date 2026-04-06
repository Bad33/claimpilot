from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.claim import Claim
from app.db.models.claim_summary import ClaimSummary
from app.db.models.document import Document
from app.db.models.extraction import Extraction
from app.utils.prompt_loader import load_prompt


@dataclass
class SummaryGenerationResult:
    summary_text: str
    model_name: str
    confidence: float
    source_snippets: list[str]


class SummarizationService:
    @staticmethod
    def _collect_document_text(documents: list[Document], max_chars: int = 12000) -> str:
        chunks: list[str] = []
        current_len = 0

        for doc in documents:
            if not doc.parsed_text:
                continue

            block = f"[Document: {doc.filename}]\n{doc.parsed_text}\n"
            if current_len + len(block) > max_chars:
                remaining = max_chars - current_len
                if remaining > 0:
                    chunks.append(block[:remaining])
                break

            chunks.append(block)
            current_len += len(block)

        return "\n\n".join(chunks).strip()

    @staticmethod
    def _collect_source_snippets(extractions: list[Extraction], limit: int = 5) -> list[str]:
        snippets: list[str] = []
        seen: set[str] = set()

        for extraction in extractions:
            if extraction.source_snippet:
                snippet = extraction.source_snippet.strip()
                if snippet and snippet not in seen:
                    snippets.append(snippet)
                    seen.add(snippet)
            if len(snippets) >= limit:
                break

        return snippets

    @staticmethod
    def _fallback_summary(claim: Claim, extractions: list[Extraction], documents: list[Document]) -> str:
        field_map = {item.field_name: item.field_value for item in extractions}

        claimant = field_map.get("claimant_name") or claim.claimant_name or "the claimant"
        incident_date = field_map.get("incident_date") or (
            str(claim.incident_date) if claim.incident_date else None
        )
        claim_type = field_map.get("claim_type") or claim.claim_type or "claim"
        claimed_amount = field_map.get("claimed_amount") or (
            str(claim.claimed_amount) if claim.claimed_amount is not None else None
        )

        narrative = ""
        for doc in documents:
            if doc.parsed_text:
                lines = [line.strip() for line in doc.parsed_text.splitlines() if line.strip()]
                non_header_lines = [
                    line for line in lines
                    if ":" not in line[:30]
                ]
                if non_header_lines:
                    narrative = " ".join(non_header_lines[:2])
                    break

        parts: list[str] = []
        intro = f"A {claim_type.lower()} claim was submitted"
        if incident_date:
            intro += f" for an incident dated {incident_date}"
        intro += f" involving {claimant}."
        parts.append(intro)

        if claimed_amount:
            parts.append(f"The reported claimed amount is ${claimed_amount}.")

        if narrative:
            parts.append(f"Document notes indicate that {narrative}")

        review_signals: list[str] = []
        lower_text = " ".join(
            [doc.parsed_text.lower() for doc in documents if doc.parsed_text]
        )

        for term in ["police report", "fire department", "injury", "legal", "attorney", "pending", "temporary relocation"]:
            if term in lower_text:
                review_signals.append(term)

        if review_signals:
            parts.append(
                "Notable review signals mentioned in the documents include "
                + ", ".join(review_signals)
                + "."
            )

        return " ".join(parts).strip()

    @classmethod
    def _openai_summary(cls, document_text: str) -> str:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        system_prompt = load_prompt("claim_summary_prompt.txt")

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Claim documents:\n\n{document_text}",
                },
            ],
        )

        return response.output_text.strip()

    @classmethod
    def generate_summary(
        cls,
        claim: Claim,
        documents: list[Document],
        extractions: list[Extraction],
    ) -> SummaryGenerationResult:
        source_snippets = cls._collect_source_snippets(extractions)
        document_text = cls._collect_document_text(documents)

        if settings.OPENAI_API_KEY.strip():
            try:
                summary_text = cls._openai_summary(document_text)
                return SummaryGenerationResult(
                    summary_text=summary_text,
                    model_name=settings.OPENAI_MODEL,
                    confidence=0.88,
                    source_snippets=source_snippets,
                )
            except Exception:
                pass

        fallback_summary = cls._fallback_summary(claim, extractions, documents)
        return SummaryGenerationResult(
            summary_text=fallback_summary,
            model_name="deterministic-fallback-v1",
            confidence=0.70,
            source_snippets=source_snippets,
        )

    @staticmethod
    def save_summary(
        db: Session,
        claim_id: int,
        summary_text: str,
        model_name: str,
        confidence: float,
        source_snippets: list[str],
    ) -> ClaimSummary:
        existing = db.query(ClaimSummary).filter(ClaimSummary.claim_id == claim_id).first()

        if existing:
            existing.summary_text = summary_text
            existing.model_name = model_name
            existing.confidence = confidence
            existing.source_snippets = source_snippets
            db.commit()
            db.refresh(existing)
            return existing

        summary = ClaimSummary(
            claim_id=claim_id,
            summary_text=summary_text,
            model_name=model_name,
            confidence=confidence,
            source_snippets=source_snippets,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary
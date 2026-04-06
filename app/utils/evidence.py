import re


def extract_evidence_snippet(text: str, matched_value: str, window: int = 120) -> str | None:
    if not text or not matched_value:
        return None

    try:
        match = re.search(re.escape(matched_value), text, flags=re.IGNORECASE)
        if not match:
            return None

        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        snippet = text[start:end].strip()

        snippet = snippet.replace("\n", " ")
        snippet = re.sub(r"\s+", " ", snippet)
        return snippet
    except Exception:
        return None
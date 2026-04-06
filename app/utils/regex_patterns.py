CLAIM_NUMBER_PATTERNS = [
    r"Claim\s*(?:Number|No\.?|#)\s*:\s*([A-Z0-9\-]+)",
    r"Claim ID\s*:\s*([A-Z0-9\-]+)",
]

CLAIMANT_NAME_PATTERNS = [
    r"Claimant\s*Name\s*:\s*([A-Z][A-Za-z\s\.\-']+)",
    r"Insured\s*Name\s*:\s*([A-Z][A-Za-z\s\.\-']+)",
    r"Name\s*:\s*([A-Z][A-Za-z\s\.\-']+)",
]

INCIDENT_DATE_PATTERNS = [
    r"Incident\s*Date\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
    r"Date\s*of\s*Loss\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
    r"Loss\s*Date\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
]

CLAIM_TYPE_PATTERNS = [
    r"Claim\s*Type\s*:\s*([A-Za-z\s\-]+)",
    r"Loss\s*Type\s*:\s*([A-Za-z\s\-]+)",
]

CLAIM_AMOUNT_PATTERNS = [
    r"Claimed\s*Amount\s*:\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
    r"Estimated\s*Damage\s*:\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
    r"Amount\s*Claimed\s*:\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
]
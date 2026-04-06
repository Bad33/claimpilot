from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_claim_summary() -> None:
    claim_payload = {
        "external_claim_id": "CLM-2026-3001",
        "claimant_name": "Emma Brooks",
        "incident_date": "2026-04-03",
        "claim_type": "property",
        "claimed_amount": 12450.00,
        "status": "new",
    }

    create_claim_response = client.post("/api/v1/claims", json=claim_payload)
    assert create_claim_response.status_code == 201
    claim_id = create_claim_response.json()["id"]

    txt_content = (
        "Claim Number: CLM-2026-3001\n"
        "Claimant Name: Emma Brooks\n"
        "Incident Date: 2026-04-03\n"
        "Claim Type: Property Damage\n"
        "Claimed Amount: $12450.00\n"
        "The claimant reported storm-related roof damage and interior water intrusion.\n"
        "Temporary relocation may be required pending contractor inspection.\n"
    )

    files = {
        "file": ("claim_summary.txt", txt_content.encode("utf-8"), "text/plain")
    }

    upload_response = client.post(f"/api/v1/claims/{claim_id}/documents", files=files)
    assert upload_response.status_code == 201

    extraction_response = client.post(f"/api/v1/claims/{claim_id}/extract")
    assert extraction_response.status_code == 200

    summary_response = client.post(f"/api/v1/claims/{claim_id}/summarize")
    assert summary_response.status_code == 200

    payload = summary_response.json()
    assert payload["claim_id"] == claim_id
    assert payload["summary_text"]
    assert payload["model_name"]
    assert payload["confidence"] > 0
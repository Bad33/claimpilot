from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_extract_claim_fields() -> None:
    claim_payload = {
        "external_claim_id": "CLM-2026-2001",
        "claimant_name": "Robert Lee",
        "incident_date": "2026-04-02",
        "claim_type": "auto",
        "claimed_amount": 7400.00,
        "status": "new",
    }

    create_claim_response = client.post("/api/v1/claims", json=claim_payload)
    assert create_claim_response.status_code == 201
    claim_id = create_claim_response.json()["id"]

    txt_content = (
        "Claim Number: CLM-2026-2001\n"
        "Claimant Name: Robert Lee\n"
        "Incident Date: 2026-04-02\n"
        "Claim Type: Auto Collision\n"
        "Claimed Amount: $7400.00\n"
        "The claimant reported front-end damage after a highway collision.\n"
    )

    files = {
        "file": ("claim_extract.txt", txt_content.encode("utf-8"), "text/plain")
    }

    upload_response = client.post(f"/api/v1/claims/{claim_id}/documents", files=files)
    assert upload_response.status_code == 201

    extract_response = client.post(f"/api/v1/claims/{claim_id}/extract")
    assert extract_response.status_code == 200

    payload = extract_response.json()
    assert payload["claim_id"] == claim_id
    assert payload["total_extractions"] >= 5

    fields = {item["field_name"]: item["field_value"] for item in payload["extracted_fields"]}

    assert fields["claim_number"] == "CLM-2026-2001"
    assert fields["claimant_name"] == "Robert Lee"
    assert fields["incident_date"] == "2026-04-02"
    assert fields["claim_type"] == "Auto Collision"
    assert fields["claimed_amount"] == "7400.00"
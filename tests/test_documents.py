from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_document_to_claim() -> None:
    claim_payload = {
        "external_claim_id": "CLM-2026-1001",
        "claimant_name": "Alice Morgan",
        "incident_date": "2026-04-01",
        "claim_type": "property",
        "claimed_amount": 5800.00,
        "status": "new",
    }

    create_response = client.post("/api/v1/claims", json=claim_payload)
    assert create_response.status_code == 201
    claim_id = create_response.json()["id"]

    txt_content = (
        "Claim Number: CLM-2026-1001\n"
        "Claimant Name: Alice Morgan\n"
        "Incident Date: 2026-04-01\n"
        "Claim Type: Property Damage\n"
        "Claimed Amount: $5800.00\n"
        "Water leak caused ceiling damage in kitchen.\n"
    )

    files = {
        "file": ("claim_notice.txt", txt_content.encode("utf-8"), "text/plain")
    }

    upload_response = client.post(f"/api/v1/claims/{claim_id}/documents", files=files)
    assert upload_response.status_code == 201

    uploaded = upload_response.json()
    assert uploaded["claim_id"] == claim_id
    assert uploaded["filename"] == "claim_notice.txt"
    assert uploaded["file_type"] == "txt"
    assert "Alice Morgan" in uploaded["parsed_text"]
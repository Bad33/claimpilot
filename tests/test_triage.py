from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_run_claim_triage() -> None:
    claim_payload = {
        "external_claim_id": "CLM-2026-5001",
        "claimant_name": "Sarah Mitchell",
        "incident_date": "2026-04-05",
        "claim_type": "property",
        "claimed_amount": 28000.00,
        "status": "new",
    }

    create_claim_response = client.post("/api/v1/claims", json=claim_payload)
    assert create_claim_response.status_code == 201
    claim_id = create_claim_response.json()["id"]

    txt_content = (
        "Claim Number: CLM-2026-5001\n"
        "Claimant Name: Sarah Mitchell\n"
        "Incident Date: 2026-04-05\n"
        "Claim Type: Property Damage\n"
        "Claimed Amount: $28000.00\n"
        "Kitchen fire caused heavy smoke damage.\n"
        "Fire department responded. Temporary relocation may be required.\n"
        "Additional contractor estimates are pending.\n"
    )

    files = {
        "file": ("claim_triage.txt", txt_content.encode("utf-8"), "text/plain")
    }

    upload_response = client.post(f"/api/v1/claims/{claim_id}/documents", files=files)
    assert upload_response.status_code == 201

    extraction_response = client.post(f"/api/v1/claims/{claim_id}/extract")
    assert extraction_response.status_code == 200

    triage_response = client.post(f"/api/v1/claims/{claim_id}/triage")
    assert triage_response.status_code == 200

    payload = triage_response.json()
    assert payload["claim_id"] == claim_id
    assert payload["complexity_label"] in {"low", "medium", "high"}
    assert payload["routing_label"] in {"low_touch", "adjuster_review", "escalate"}
    assert payload["routing_confidence"] > 0
    assert isinstance(payload["reason_codes"], list)
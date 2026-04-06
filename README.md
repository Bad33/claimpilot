# ClaimPilot

**ClaimPilot** is an explainable AI claims triage and document intelligence platform for insurance workflows.

It ingests claim-related documents, extracts structured claim fields, generates grounded claim summaries, predicts claim complexity, recommends routing, and stores evidence-backed outputs with audit logs.

This project is designed as a portfolio-ready AI engineering system that demonstrates:
- document intelligence
- LLM-assisted summarization
- interpretable ML classification
- rules-based routing
- explainability
- auditability
- full-stack workflow visualization

---

## Why this project

Insurance claims operations rely heavily on documents, structured field extraction, triage decisions, and traceable review workflows.

ClaimPilot was built to simulate a realistic claims intake and triage platform where:
- documents are uploaded and parsed
- important fields are extracted
- summaries are generated from source-grounded text
- complexity is predicted using ML
- routing is recommended using rules + model outputs
- every step leaves an audit trail

This is not a generic chatbot wrapper.  
It is an AI-backed operational workflow system.

---

## Core features

### Document intake
- Upload claim-related documents in **TXT** or **PDF** format
- Parse and normalize text for downstream processing
- Store document metadata and parsed text in PostgreSQL

### Structured field extraction
Extracts key insurance claim fields such as:
- claim number
- claimant name
- incident date
- claim type
- claimed amount

Each extracted field includes:
- confidence score
- extraction method
- source snippet evidence

### Grounded claim summarization
- Generates a concise claim summary from uploaded documents
- Uses OpenAI when configured
- Falls back to a deterministic local summary when no API key is available
- Stores supporting snippets for explainability

### Claim complexity prediction
- Uses a scikit-learn **LogisticRegression** model
- Predicts claim complexity as:
  - `low`
  - `medium`
  - `high`

### Routing recommendation
Combines:
- rule-based logic
- model complexity prediction
- confidence checks

Recommended routes:
- `low_touch`
- `adjuster_review`
- `escalate`

### Explainability and auditability
Stores:
- extraction source snippets
- summary source snippets
- triage reason codes
- review flags
- feature snapshots
- audit logs

### Frontend demo app
A lightweight React frontend is included to demo the full workflow:
1. create claim
2. upload document
3. run extraction
4. generate summary
5. run triage
6. inspect audit trail

---

## Tech stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- OpenAI API
- scikit-learn
- pandas
- numpy
- joblib

### Frontend
- React
- Vite

### Infrastructure
- Docker
- Docker Compose

---

## Project structure

```text
claimpilot/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── audit.py
│   │       ├── claim_detail.py
│   │       ├── claims.py
│   │       ├── documents.py
│   │       ├── extractions.py
│   │       ├── health.py
│   │       ├── summaries.py
│   │       └── triage.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── audit_log.py
│   │       ├── claim.py
│   │       ├── claim_summary.py
│   │       ├── document.py
│   │       ├── extraction.py
│   │       └── triage_result.py
│   ├── ml/
│   │   ├── artifacts/
│   │   └── train.py
│   ├── schemas/
│   │   ├── audit.py
│   │   ├── claim.py
│   │   ├── claim_detail.py
│   │   ├── common.py
│   │   ├── document.py
│   │   ├── extraction.py
│   │   ├── summary.py
│   │   └── triage.py
│   ├── services/
│   │   ├── audit_service.py
│   │   ├── complexity_model_service.py
│   │   ├── document_parser.py
│   │   ├── extraction_service.py
│   │   ├── feature_service.py
│   │   ├── routing_service.py
│   │   ├── summarization_service.py
│   │   └── triage_service.py
│   ├── utils/
│   │   ├── evidence.py
│   │   ├── prompt_loader.py
│   │   ├── regex_patterns.py
│   │   └── text.py
│   └── main.py
├── data/
│   ├── sample_claims/
│   └── training/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
├── prompts/
│   └── claim_summary_prompt.txt
├── scripts/
│   ├── evaluate_model.py
│   └── train_model.py
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
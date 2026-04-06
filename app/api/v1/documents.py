from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.claim import Claim
from app.db.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.audit_service import AuditService
from app.services.document_parser import DocumentParserService, DocumentParsingError

router = APIRouter(prefix="/api/v1/claims", tags=["documents"])

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/{claim_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    claim_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Document:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 5 MB MVP upload limit.",
        )

    try:
        file_type, parsed_text = DocumentParserService.parse(file.filename, file_bytes)
    except DocumentParsingError as exc:
        AuditService.log_event(
            db=db,
            event_type="document_upload_failed",
            actor="api",
            claim_id=claim_id,
            event_payload={
                "filename": file.filename,
                "reason": str(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    document = Document(
        claim_id=claim_id,
        filename=file.filename,
        file_type=file_type,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(file_bytes),
        raw_text=parsed_text,
        parsed_text=parsed_text,
        parse_status="parsed",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    AuditService.log_event(
        db=db,
        event_type="document_uploaded",
        actor="api",
        claim_id=claim_id,
        event_payload={
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "parse_status": document.parse_status,
        },
    )

    return document


@router.get("/{claim_id}/documents", response_model=list[DocumentResponse])
def list_documents(claim_id: int, db: Session = Depends(get_db)) -> list[Document]:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id '{claim_id}' not found.",
        )

    documents = (
        db.query(Document)
        .filter(Document.claim_id == claim_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return documents
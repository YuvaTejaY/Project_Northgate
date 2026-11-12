from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentStatusResponse, DocumentUploadResponse
from app.services.audit_service import add_audit_log
from app.services.document_service import DocumentService
from app.utils.permissions import require_roles
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    customer_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> dict:
    document = DocumentService.upload_document(db, customer_id=customer_id, file=file, uploaded_by=str(current_user.id))
    add_audit_log(
        db,
        user_id=current_user.id,
        action="document_uploaded",
        entity_id=str(document.id),
        new_value=f"customer={customer_id};file={document.file_name}",
    )
    return document


@router.get("/{document_id}", response_model=DocumentStatusResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> dict:
    document = DocumentService.get_document(db, document_id)
    return {
        "id": str(document.id),
        "status": document.status.value,
        "file_name": document.file_name,
        "document_type": document.document_type,
        "metadata": document.document_metadata,
    }

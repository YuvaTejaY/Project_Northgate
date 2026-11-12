from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from google.cloud import storage
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document, DocumentStatus


class DocumentService:
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        allowed_types = {"application/pdf", "image/jpeg", "image/png"}
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10MB limit")

    @staticmethod
    def upload_document(db: Session, *, customer_id: str, file: UploadFile, uploaded_by: str) -> Document:
        DocumentService.validate_file(file)
        customer_uuid = UUID(str(customer_id))
        filename = file.filename or "uploaded_document"
        extension = Path(filename).suffix or ".bin"
        storage_key = f"documents/{customer_uuid}/{uuid.uuid4()}{extension}"
        content = file.file.read()
        if settings.gcs_bucket_name:
            bucket = storage.Client(project=settings.google_cloud_project).bucket(settings.gcs_bucket_name)
            bucket.blob(storage_key).upload_from_string(
                content,
                content_type=file.content_type or "application/octet-stream",
            )
            source = "google-cloud-storage"
        else:
            upload_dir = Path(__file__).resolve().parents[2] / "uploads"
            upload_dir.mkdir(exist_ok=True)
            target = upload_dir / storage_key.replace("/", "_")
            target.write_bytes(content)
            source = "local-upload"

        document = Document(
            customer_id=customer_uuid,
            file_name=filename,
            document_type="identity_document",
            storage_key=storage_key,
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(content),
            status=DocumentStatus.UPLOADED,
            document_metadata=f'{{"source": "{source}"}}',
            uploaded_by=UUID(str(uploaded_by)),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document(db: Session, document_id: str) -> Document:
        document_uuid = UUID(str(document_id))
        document = db.query(Document).filter(Document.id == document_uuid).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document

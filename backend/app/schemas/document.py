from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadResponse(BaseModel):
    id: UUID
    customer_id: UUID
    file_name: str
    document_type: str
    storage_key: str
    mime_type: str
    file_size_bytes: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentStatusResponse(BaseModel):
    id: UUID
    status: str
    file_name: str
    document_type: str
    metadata: str | dict | None = None

    model_config = ConfigDict(from_attributes=True)

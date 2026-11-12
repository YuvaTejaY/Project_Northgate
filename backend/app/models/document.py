import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentStatus(str, Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    VERIFIED = "Verified"
    REJECTED = "Rejected"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    document_type = Column(String(80), nullable=False)
    storage_key = Column(String(255), nullable=False)
    mime_type = Column(String(80), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    document_metadata = Column(Text, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="documents")

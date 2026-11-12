import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class VerificationStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    VERIFIED = "Verified"
    DISCREPANCY_FOUND = "Discrepancy Found"
    MANUAL_REVIEW_REQUIRED = "Manual Review Required"
    REJECTED = "Rejected"


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    status = Column(SQLAlchemyEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    trigger = Column(String(120), nullable=False, default="manual")
    summary = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=True)
    comparison_results = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="verifications")

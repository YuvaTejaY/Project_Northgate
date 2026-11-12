import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CustomerStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "Processing"
    VERIFIED = "Verified"
    DISCREPANCY_FOUND = "Discrepancy Found"
    MANUAL_REVIEW_REQUIRED = "Manual Review Required"
    REJECTED = "Rejected"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    date_of_birth = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    onboarding_status = Column(SQLAlchemyEnum(CustomerStatus), default=CustomerStatus.PENDING, nullable=False)
    address = Column(Text, nullable=True)
    nationality = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="customers")
    documents = relationship("Document", back_populates="customer", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="customer", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="customer", cascade="all, delete-orphan")
    analyst_decisions = relationship("AnalystDecision", back_populates="customer", cascade="all, delete-orphan")

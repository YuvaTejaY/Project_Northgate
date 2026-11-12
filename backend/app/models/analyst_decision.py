import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AnalystDecisionType(str, Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
    REQUEST_MORE_INFO = "Request More Information"


class AnalystDecision(Base):
    __tablename__ = "analyst_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    decision = Column(SQLAlchemyEnum(AnalystDecisionType), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="analyst_decisions")
    user = relationship("User", back_populates="analyst_decisions")

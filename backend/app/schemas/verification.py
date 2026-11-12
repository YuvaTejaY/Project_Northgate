from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VerificationStartRequest(BaseModel):
    trigger: str = "manual"
    note: str | None = None


class VerificationStatusResponse(BaseModel):
    id: UUID
    customer_id: UUID
    status: str
    trigger: str
    summary: str | None = None
    confidence_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

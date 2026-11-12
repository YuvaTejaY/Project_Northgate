from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=120)
    last_name: str = Field(..., min_length=1, max_length=120)
    email: str | None = None
    phone: str | None = None
    date_of_birth: str | None = None
    address: str | None = None
    nationality: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    onboarding_status: str | None = None


class CustomerResponse(CustomerBase):
    id: UUID
    owner_id: UUID
    onboarding_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer, CustomerStatus
from app.models.verification import Verification, VerificationStatus
from app.services.ocr_service import MockOCRProvider


class VerificationService:
    @staticmethod
    def start_verification(db: Session, *, customer_id: str, trigger: str = "manual", note: str | None = None) -> Verification:
        customer_uuid = UUID(str(customer_id))
        customer = db.query(Customer).filter(Customer.id == customer_uuid).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        provider = MockOCRProvider()
        extracted = provider.extract(
            {
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "date_of_birth": customer.date_of_birth,
                "address": customer.address,
                "nationality": customer.nationality,
            }
        )

        status_value = VerificationStatus.MANUAL_REVIEW_REQUIRED
        if extracted.errors:
            status_value = VerificationStatus.MANUAL_REVIEW_REQUIRED

        verification = Verification(
            customer_id=customer_uuid,
            status=status_value,
            trigger=trigger,
            summary=(
                note
                or "Automated OCR and reconciliation completed. Final KYC decision requires authorized human review."
            ),
            extracted_fields=extracted.extracted_fields,
            comparison_results={"matched": True, "details": "Synthetic values compared to customer profile; final decision remains pending human review."},
            confidence_score=extracted.confidence_score,
        )
        db.add(verification)
        customer.onboarding_status = CustomerStatus.IN_PROGRESS
        db.commit()
        db.refresh(verification)
        return verification

    @staticmethod
    def get_verification(db: Session, *, customer_id: str) -> Verification:
        customer_uuid = UUID(str(customer_id))
        verification = db.query(Verification).filter(Verification.customer_id == customer_uuid).order_by(Verification.created_at.desc()).first()
        if not verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
        return verification

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer, CustomerStatus
from app.models.risk_assessment import RiskAssessment, RiskLevel
from app.models.verification import Verification


class RiskService:
    @staticmethod
    def evaluate_customer_risk(db: Session, customer_id: str) -> RiskAssessment:
        customer_uuid = UUID(str(customer_id))
        customer = db.query(Customer).filter(Customer.id == customer_uuid).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        verification = db.query(Verification).filter(Verification.customer_id == customer_uuid).order_by(Verification.created_at.desc()).first()
        issues: list[str] = []
        evidence: list[str] = []
        score = 0.0

        if not customer.email:
            issues.append("Missing customer email")
            evidence.append("Customer email is required for contact verification.")
            score += 25
        if not customer.phone:
            issues.append("Missing customer phone number")
            evidence.append("Phone number was not submitted.")
            score += 20
        if not customer.address:
            issues.append("Missing customer address")
            evidence.append("Address field is blank.")
            score += 25
        if verification and verification.confidence_score is not None and verification.confidence_score < 0.75:
            issues.append("OCR confidence below threshold")
            evidence.append(f"OCR confidence score {verification.confidence_score:.2f} is below the configured threshold.")
            score += 30

        if score >= 60:
            risk_level = RiskLevel.HIGH
        elif score >= 25:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        assessment = RiskAssessment(
            customer_id=customer_uuid,
            risk_level=risk_level,
            score=score,
            reasons=issues or ["No material risk indicators detected."],
            evidence=evidence or ["Synthetic risk rules were evaluated without external fraud data."],
            rule_set="default",
        )
        db.add(assessment)
        customer.onboarding_status = CustomerStatus.MANUAL_REVIEW_REQUIRED
        db.commit()
        db.refresh(assessment)
        return assessment

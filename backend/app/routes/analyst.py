from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analyst_decision import AnalystDecision, AnalystDecisionType
from app.models.customer import Customer, CustomerStatus
from app.models.user import User
from app.schemas.customer import CustomerResponse
from app.services.audit_service import add_audit_log
from app.utils.permissions import require_roles

router = APIRouter()


@router.get("/pending", response_model=list[CustomerResponse])
def pending_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> list[Customer]:
    return db.query(Customer).filter(Customer.onboarding_status.in_([CustomerStatus.PENDING, CustomerStatus.IN_PROGRESS])).all()


@router.get("/manual-review", response_model=list[CustomerResponse])
def manual_review_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> list[Customer]:
    return db.query(Customer).filter(Customer.onboarding_status == CustomerStatus.MANUAL_REVIEW_REQUIRED).all()


@router.get("/verified", response_model=list[CustomerResponse])
def verified_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> list[Customer]:
    return db.query(Customer).filter(Customer.onboarding_status == CustomerStatus.VERIFIED).all()


@router.get("/discrepancies", response_model=list[CustomerResponse])
def discrepancy_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> list[Customer]:
    return db.query(Customer).filter(Customer.onboarding_status == CustomerStatus.DISCREPANCY_FOUND).all()


@router.get("/customer/{customer_id}")
def get_customer_details(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> dict[str, Any]:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return {
        "customer": customer,
        "documents": customer.documents,
        "verification": customer.verifications[-1] if customer.verifications else None,
        "risk_assessment": customer.risk_assessments[-1] if customer.risk_assessments else None,
    }


@router.post("/{customer_id}/decision")
def submit_decision(
    customer_id: str,
    decision: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> dict[str, str]:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    decision_type = AnalystDecisionType(decision)
    record = AnalystDecision(
        customer_id=customer_id,
        user_id=current_user.id,
        decision=decision_type,
        reason=reason,
    )
    db.add(record)
    if decision_type == AnalystDecisionType.APPROVE:
        customer.onboarding_status = CustomerStatus.VERIFIED
    elif decision_type == AnalystDecisionType.REJECT:
        customer.onboarding_status = CustomerStatus.REJECTED
    else:
        customer.onboarding_status = CustomerStatus.MANUAL_REVIEW_REQUIRED
    db.commit()
    add_audit_log(
        db,
        user_id=current_user.id,
        action="analyst_decision",
        entity_id=str(customer.id),
        previous_value=customer.onboarding_status.value,
        new_value=decision_type.value,
        reason=reason,
    )
    return {"message": "decision recorded", "decision": decision_type.value}

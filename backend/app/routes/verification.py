from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.verification import VerificationStartRequest, VerificationStatusResponse
from app.services.audit_service import add_audit_log
from app.services.verification_service import VerificationService
from app.utils.permissions import require_roles

router = APIRouter()


@router.post("/{customer_id}/start", response_model=VerificationStatusResponse, status_code=status.HTTP_201_CREATED)
def start_verification(
    customer_id: str,
    payload: VerificationStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> dict:
    verification = VerificationService.start_verification(
        db,
        customer_id=customer_id,
        trigger=payload.trigger,
        note=payload.note,
    )
    add_audit_log(
        db,
        user_id=current_user.id,
        action="verification_started",
        entity_id=str(verification.id),
        new_value=f"customer={customer_id};status={verification.status.value}",
    )
    return {
        "id": str(verification.id),
        "customer_id": str(verification.customer_id),
        "status": verification.status.value,
        "trigger": verification.trigger,
        "summary": verification.summary,
        "confidence_score": verification.confidence_score,
        "created_at": verification.created_at,
        "updated_at": verification.updated_at,
    }


@router.get("/{customer_id}/status", response_model=VerificationStatusResponse)
def get_verification_status(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> dict:
    verification = VerificationService.get_verification(db, customer_id=customer_id)
    return {
        "id": str(verification.id),
        "customer_id": str(verification.customer_id),
        "status": verification.status.value,
        "trigger": verification.trigger,
        "summary": verification.summary,
        "confidence_score": verification.confidence_score,
        "created_at": verification.created_at,
        "updated_at": verification.updated_at,
    }

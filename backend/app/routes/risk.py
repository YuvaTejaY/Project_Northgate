from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.audit_service import add_audit_log
from app.services.risk_service import RiskService
from app.utils.permissions import require_roles

router = APIRouter()


@router.get("/{customer_id}")
def get_customer_risk(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> dict:
    assessment = RiskService.evaluate_customer_risk(db, customer_id)
    add_audit_log(
        db,
        user_id=current_user.id,
        action="risk_assessed",
        entity_id=str(assessment.id),
        new_value=f"customer={customer_id};risk={assessment.risk_level.value};score={assessment.score}",
    )
    return {
        "id": str(assessment.id),
        "customer_id": customer_id,
        "risk_level": assessment.risk_level.value,
        "score": assessment.score,
        "reasons": assessment.reasons,
        "evidence": assessment.evidence,
        "rule_set": assessment.rule_set,
    }

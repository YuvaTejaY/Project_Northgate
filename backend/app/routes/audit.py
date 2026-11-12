from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.permissions import require_roles

router = APIRouter()


@router.get("/", response_model=list[dict])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst")),
) -> list[dict]:
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": str(row.id),
            "user_id": str(row.user_id),
            "action": row.action,
            "timestamp": row.timestamp.isoformat(),
            "entity_id": row.entity_id,
            "previous_value": row.previous_value,
            "new_value": row.new_value,
            "reason": row.reason,
            "request_correlation_id": row.request_correlation_id,
        }
        for row in rows
    ]

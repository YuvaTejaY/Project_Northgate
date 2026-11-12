from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def add_audit_log(
    db: Session,
    *,
    user_id: UUID | str,
    action: str,
    entity_id: str | None = None,
    previous_value: str | None = None,
    new_value: str | None = None,
    reason: str | None = None,
    request_correlation_id: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        timestamp=datetime.utcnow(),
        entity_id=entity_id,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
        request_correlation_id=request_correlation_id,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

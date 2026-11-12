from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.audit_service import add_audit_log
from app.services.customer_service import CustomerService
from app.utils.permissions import require_roles
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> Any:
    customer = CustomerService.create_customer(db, owner_id=current_user.id, data=payload.model_dump())
    add_audit_log(
        db,
        user_id=current_user.id,
        action="customer_created",
        entity_id=str(customer.id),
        new_value=payload.model_dump_json(),
    )
    return customer


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> list:
    return CustomerService.list_customers(db, skip=skip, limit=limit, owner_id=current_user.id)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> Any:
    customer = CustomerService.get_customer(db, customer_id)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "analyst", "reviewer")),
) -> Any:
    customer = CustomerService.update_customer(db, customer_id, payload=payload.model_dump(exclude_unset=True))
    add_audit_log(
        db,
        user_id=current_user.id,
        action="customer_updated",
        entity_id=str(customer.id),
        previous_value="customer update",
        new_value=payload.model_dump_json(exclude_unset=True),
    )
    return customer

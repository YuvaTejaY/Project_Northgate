from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer, CustomerStatus
from app.models.user import User


class CustomerService:
    @staticmethod
    def create_customer(db: Session, *, owner_id: UUID | str, data: dict) -> Customer:
        owner_uuid = UUID(str(owner_id))
        customer = Customer(owner_id=owner_uuid, **data)
        customer.onboarding_status = CustomerStatus.PENDING
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def list_customers(db: Session, *, skip: int = 0, limit: int = 50, owner_id: UUID | str | None = None) -> list[Customer]:
        query = db.query(Customer)
        if owner_id:
            query = query.filter(Customer.owner_id == UUID(str(owner_id)))
        return query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_customer(db: Session, customer_id: UUID | str) -> Customer:
        customer_uuid = UUID(str(customer_id))
        customer = db.query(Customer).filter(Customer.id == customer_uuid).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    @staticmethod
    def update_customer(db: Session, customer_id: UUID | str, *, payload: dict) -> Customer:
        customer = CustomerService.get_customer(db, customer_id)
        for key, value in payload.items():
            if value is not None and hasattr(customer, key):
                setattr(customer, key, value)
        customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(customer)
        return customer

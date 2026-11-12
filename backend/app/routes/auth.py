from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.audit_service import add_audit_log
from app.utils.permissions import require_roles
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if not settings.allow_public_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled. Contact your Northgate administrator.",
        )
    user = AuthService.register_user(
        db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
    )
    add_audit_log(
        db,
        user_id=user.id,
        action="user_registered",
        entity_id=str(user.id),
        new_value=f"email={user.email};role={user.role.value}",
    )
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> dict[str, str]:
    user = AuthService.authenticate_user(db, email=payload.email, password=payload.password)
    access_token, refresh_token = AuthService.create_tokens_for_user(db, user)
    add_audit_log(
        db,
        user_id=user.id,
        action="login",
        entity_id=str(user.id),
        new_value="login-success",
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    access_token, refresh_token = AuthService.refresh_tokens(db, payload.refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    payload: RefreshTokenRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    AuthService.logout(db, current_user, payload.refresh_token if payload else None)
    add_audit_log(
        db,
        user_id=current_user.id,
        action="logout",
        entity_id=str(current_user.id),
        new_value="logout-success",
    )
    return {"message": "logged out successfully"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

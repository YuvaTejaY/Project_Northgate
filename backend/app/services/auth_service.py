from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import RefreshToken, User, UserRole
from app.utils.security import create_access_token, create_refresh_token, get_password_hash, verify_password


class AuthService:
    @staticmethod
    def register_user(db: Session, *, email: str, full_name: str, password: str, role: str) -> User:
        existing = db.query(User).filter(User.email == email.lower()).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole(role),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, *, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
        return user

    @staticmethod
    def create_tokens_for_user(db: Session, user: User) -> tuple[str, str]:
        access_token = create_access_token(str(user.id), user.role.value)
        refresh_token = create_refresh_token(str(user.id), user.role.value)
        expires_at = datetime.utcnow() + timedelta(days=7)
        token_record = RefreshToken(user_id=user.id, token_hash=refresh_token, expires_at=expires_at)
        db.add(token_record)
        db.commit()
        return access_token, refresh_token

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
        token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == refresh_token).first()
        if not token_record or token_record.revoked or token_record.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired")
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        token_record.revoked = True
        return AuthService.create_tokens_for_user(db, user)

    @staticmethod
    def logout(db: Session, user: User, refresh_token: str | None = None) -> None:
        if refresh_token:
            token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == refresh_token).first()
            if token_record:
                token_record.revoked = True
        else:
            for token_record in db.query(RefreshToken).filter(RefreshToken.user_id == user.id).all():
                token_record.revoked = True
        db.commit()

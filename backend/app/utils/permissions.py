from typing import Iterable

from fastapi import Depends, HTTPException, status

from app.models.user import User, UserRole
from app.utils.security import get_current_user


def require_roles(*allowed_roles: str):
    allowed = {role.lower() for role in allowed_roles}

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        role_name = current_user.role.value.lower() if isinstance(current_user.role, UserRole) else str(current_user.role).lower()
        if role_name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return _checker

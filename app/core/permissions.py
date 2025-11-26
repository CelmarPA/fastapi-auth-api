from fastapi import Depends, HTTPException, status
from ..models import User
from .security import get_current_user


def require_role(required: str):
    """
    Allows access based on the user's role.
    Allowed roles:
    - superadmin
    - admin
    - user
    """
    def wrapper(current_user: User = Depends(get_current_user)):
        allowed = {
            "superadmin": ["superadmin", "admin", "user"],
            "admin": ["admin", "user"],
            "user": ["user"],
        }

        if current_user.role not in allowed[required]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this route."
            )

        return current_user

    return wrapper

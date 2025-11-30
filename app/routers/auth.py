# app/routers/auth.py
from fastapi import APIRouter, Depends, Request, Body, status, HTTPException
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.tokens import create_email_verification_token
from app.database import get_db
from app.core.security import get_current_user
from app.core.rate_limit import limiter
from app.core.config import settings
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth_schema import LogoutRequest
from app.schemas.token_schema import RefreshTokenRequest
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

from app.schemas import (
    UserCreate, UserResponse, Login, Token, Message,
    PasswordResetRequest, PasswordResetInput
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user. First user => superadmin, second => admin, rest => user.
    """

    try:
        user = AuthService.register(
            db=db,
            email=user_data.email,
            password=user_data.password,
            request=request
        )

        return user

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    user_data: Login,
    db: Session = Depends(get_db)
):
    """
    Login with email + password. Returns access + refresh tokens.
    Rate-limited by decorator.
    """

    try:
        result = AuthService.login(
            db,
            email=user_data.email,
            password=user_data.password,
            ip=request.client.host,
            request=request)

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)) -> Token:
    """
    Rotate refresh token and return new access + refresh token.
    """

    try:
        result = AuthService.refresh(
            db=db,
            refresh_token=payload.refresh_token,
            request=request
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/logout", response_model=Message)
def logout(data: LogoutRequest, request: Request, db: Session = Depends(get_db)) -> Message:
    """
    Logout by revoking the provided refresh token.
    """

    try:
        result = AuthService.logout(
            db=db,
            refresh_token=data.refresh_token,
            request=request
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/request-password-reset", response_model=Message)
def request_password_reset(data: PasswordResetRequest, request: Request, db: Session = Depends(get_db)) -> Message:
    """
    Request a password reset. Always returns success-like message (doesn't reveal existence).
    """

    try:
        result = AuthService.request_password_reset(
            db=db,
            email=data.email,
            request=request
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/reset-password", response_model=Message)
def reset_password(data: PasswordResetInput, request: Request, db: Session = Depends(get_db)) -> Message:
    """
    Reset password using token and new_password.
    """
    try:
        result = AuthService.reset_password(
            db=db,
            token=data.token,
            new_password=data.new_password,
            request=request
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    """
    Return current authenticated user (AuthService.get_current_user should be a dependency wrapper).
    """

    return current_user


@router.post("/send-verification-email", response_model=Message)
def send_email_verification(email: EmailStr = Body(...), db: Session = Depends(get_db)):
    email = str(email).lower().strip()

    user = UserRepository.get_by_email(db, email)

    if not user:
        return {"detail": "If the email exists, verification email was sent"}

    if user.is_verified:
        return {"detail": "Email already verified"}

    token = create_email_verification_token(user.id)

    EmailService.send_verification_email(user.email, token)

    return {"detail": "Verification email sent"}


@router.get("/verify-email", response_model=Message)
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload["sub"])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or expired token: {e}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()
    db.refresh(user)

    return {"detail": "Email verified successfully"}

# @router.post("/admin/dashboard")
# def admin_dashboard(current_user: User = Depends(require_role("admin"))):
#     return {"message": f"Welcome admin {current_user.email}"}
#
#
# @router.post("/super/secret")
# def secret_area(current_user: User = Depends(require_role("superadmin"))):
#     return {"secret": "Top level info"}
#
#
# @router.post("/user/profile")
# def user_profile(current_user: User = Depends(require_role("user"))):
#     return {"email": current_user.email, "role": current_user.role}
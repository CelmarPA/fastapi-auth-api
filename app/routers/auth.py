from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address

from ..core.bruteforce import clear_failures, record_login_attempts
from ..core.rate_limit_custom import too_many_resets_email, too_many_resets_ip, log_reset_attempt
from ..core.email import send_email
from ..core.rate_limit import limiter
from ..core.reset import create_reset_token, mark_token_used, verify_reset_token
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Login, Token, Message, PasswordResetRequest, PasswordResetInput
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..core.permissions import require_role
from ..core.tokens import generate_refresh_token_plain, hash_token, make_refresh_record

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:

    # Checks if the email already exists
    existing_user = db.query(User).filter(user_data.email == User.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Count number of existing users
    user_count = db.query(User).count()

    if user_count == 0:
        role = "superadmin"

    elif user_count == 1:
        role = "admin"

    else:
        role = "user"

    # Create new user
    new_user = User(
        email = user_data.email,
        hashed_password= hash_password(user_data.password),
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user_data: Login, db: Session = Depends(get_db)) -> Token:

    client_ip = request.client.host
    email = user_data.email.lower().strip()

    # 1. Anti-bruteforce - IP
    if too_many_resets_ip(db, client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts from this IP. Try again later."
        )

    # 2. Anti-bruteforce - Email
    if too_many_resets_email(db, user_data.email):
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts for this email. Try again later."
        )

    # Fetch user
    user = db.query(User).filter(User.email == user_data.email).first()

    # User does not exist or Incorrect password  → logs failure before returning error
    if not user or not verify_password(user_data.password, user.hashed_password):
        record_login_attempts(db, email, client_ip, success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Login Ok - Clear failures
    clear_failures(db, user_data.email, client_ip)

    # Register success
    record_login_attempts(db, user_data.email, client_ip, success=True)

    # Create Tokens
    token = create_access_token({"sub": str(user.id), "role": user.role})

    # Creates an opaque refresh token and stores its hash.
    plain_refresh = generate_refresh_token_plain()
    make_refresh_record(db, user.id, plain_refresh)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "refresh_token": plain_refresh
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)) -> Token:
    from ..models import RefreshToken

    token_hash = hash_token(refresh_token)
    token_rec = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    # If it doesn't exist -> possible reuse (token already used and removed)
    if not token_rec:
        # Revoke all refresh tokens for the user if possible.
        # We don't have a user_id here: impossible to identify, so generic response.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # If expired or already revoked => possible reuse
    now = datetime.now(timezone.utc)

    expires_at = token_rec.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if token_rec.revoked or expires_at < now:
        # Revoke all tokens for this user (mitigation)
        db.query(RefreshToken).filter(RefreshToken.user_id == token_rec.user_id).update({"revoked": True})
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired"
        )

    # Valid token -> rotate
    # Create new refresh token
    new_plain = generate_refresh_token_plain()
    new_rec = make_refresh_record(db, token_rec.user_id, new_plain)

    # mark current token as revoked and specify replaced_by
    token_rec.revoked = True
    token_rec.replaced_by = new_rec.id
    db.add(token_rec)
    db.commit()

    # Create new access token
    access = create_access_token({"sub": str(token_rec.user_id)})

    return {
        "access_token": access,
        "token_type": "Bearer",
        "refresh_token": new_plain
    }


@router.post("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {current_user.email}"}


@router.post("/super/secret")
def secret_area(current_user: User = Depends(require_role("superadmin"))):
    return {"secret": "Top level info"}


@router.post("/user/profile")
def user_profile(current_user: User = Depends(require_role("user"))):
    return {"email": current_user.email, "role": current_user.role}


@router.post("/request-password-reset")
def request_password_reset(request: Request, data: PasswordResetRequest, db: Session = Depends(get_db)) -> Message:
    client_ip = request.client.host

    # 1. Rate-limit by IP
    if too_many_resets_ip(db, client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many reset attempts from this IP. Try again later."
        )

    # 2. Rate-limit by email
    if too_many_resets_email(db, data.email):
        raise HTTPException(
            status_code=429,
            detail="Too many password reset attempts for this email. Try again later."
        )

    # Save log
    log_reset_attempt(db, data.email, client_ip)

    # Search User
    user = db.query(User).filter(User.email ==  data.email).first()

    # Security: does not reveal if the email exists
    if not user:
        return {"detail": "If this email exists, a reset link has been sent."}

    token = create_reset_token(db, user.id)

    # For now, we're just printing the link to the console.
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    html = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        <br></br>
        <p>If you did not request this,please ignore this email.</p>
    """

    send_email(user.email, "Password Reset", html)

    return {"detail": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: PasswordResetInput, db: Session = Depends(get_db)) -> Message:
    user = verify_reset_token(db, data.token)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    # Update password
    user.hashed_password = hash_password(data.new_password)
    db.commit()

    # mark token as used
    mark_token_used(db, data.token)

    return {"detail": "Password has been reset successfully"}


@router.post("/logout")
def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)) -> Message:
    from ..models import RefreshToken
    token_hash = hash_token(refresh_token)
    rec = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not rec:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # revoke only this token (or all of the user's tokens if preferred)
    rec.revoked = True
    db.add(rec)
    db.commit()

    return {
        "detail": "Logged out"
    }

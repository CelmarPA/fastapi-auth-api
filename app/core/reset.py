import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session


from ..models import ResetToken, User
from .security import hash_password
from .tokens import hash_token

RESET_TOKEN_EXPIRE_MINUTES = 15


def create_reset_token(db: Session, user_id: int) -> str:
    # Plain token
    token = secrets.token_urlsafe(48)
    token_hash = hash_token(token)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    reset = ResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )

    db.add(reset)
    db.commit()
    db.refresh(reset)

    return token    # return plain token to send by email


def verify_reset_token(db: Session, token: str) -> User:
    token_hash = hash_token(token)

    rec = db.query(ResetToken).filter(
        ResetToken.token_hash == token_hash,
        ResetToken.used == False
    ).first()

    if not rec:
        return None

    expires_at = rec.expires_at

    # Fix timezone if missing
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return None

    return rec.user


def mark_token_used(db: Session, token: str) -> None:
    token_hash = hash_token(token)
    rec = db.query(ResetToken).filter(ResetToken.token_hash == token_hash).first()

    if rec:
        rec.used = True
        db.commit()


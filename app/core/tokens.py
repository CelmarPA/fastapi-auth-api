import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.models import RefreshToken


REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def generate_refresh_token_plain() -> str:
    plain = secrets.token_urlsafe(48)

    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    return {
        "plain": plain,
        "hash": hash_token(plain),
        "expires_at": expires_at
    }


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def make_refresh_record(db, user_id: int, plain_token: str) -> RefreshToken:
    token_hash = hash_token(plain_token)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    rec = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires,
        revoked=False,
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec


def create_email_verification_token(user_id: int):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
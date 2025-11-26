import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from ..core.config import settings
from ..models import RefreshToken


REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def generate_refresh_token_plain() -> str:
    # secure opaque token
    return secrets.token_urlsafe(64)


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
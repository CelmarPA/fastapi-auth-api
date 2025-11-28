from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import ResetToken
from app.core.tokens import hash_token


class ResetRepository:

    @staticmethod
    def create(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> ResetToken:
        rec = ResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        db.add(rec)
        db.commit()
        db.refresh(rec)

        return rec

    @staticmethod
    def get_valid(db: Session, token: str) -> ResetToken:
        token_hash = hash_token(token)
        now = datetime.now(timezone.utc)

        reset_token = db.query(ResetToken).filter(
            ResetToken.token_hash == token_hash,
            ResetToken.used == False,
            ResetToken.expires_at >= now
        ).first()

        return reset_token

    @staticmethod
    def mark_used(db: Session, token: str) -> ResetToken:
        token_hash = hash_token(token)
        rec = db.query(ResetToken).filter(
            ResetToken.token_hash == token_hash
        ).first()

        if rec:
            rec.used = True
            db.commit()

        return rec

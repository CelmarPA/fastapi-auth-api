import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models import ResetToken
from app.repositories import ResetRepository, UserRepository
from app.core.tokens import hash_token

RESET_EXPIRE_MINUTES = 15


class ResetService:

    @staticmethod
    def create_reset_token(db: Session, user_id: int) -> ResetToken:
        plain = secrets.token_urlsafe(48)
        token_hash = hash_token(plain)

        expires = datetime.now(timezone.utc) + timedelta(minutes=RESET_EXPIRE_MINUTES)

        ResetRepository.create(db, user_id, token_hash, expires)

        return plain

    @staticmethod
    def verify_reset_token(db: Session, token: str) -> UserRepository:
        record = ResetRepository.get_valid(db, token)

        if not record:
            return None

        return UserRepository.get_by_id(db, record.user_id)

    @staticmethod
    def mark_used(db: Session, token: str) -> bool:
        return ResetRepository.mark_used(db, token)

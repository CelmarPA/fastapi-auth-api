from sqlalchemy.orm import Session
from datetime import datetime

from app.models import RefreshToken
from app.core.tokens import hash_token


class TokenRepository:

    @staticmethod
    def create_refresh(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        db.add(token)
        db.commit()
        db.refresh(token)

        return token

    @staticmethod
    def get_by_plain(db: Session, refresh_token: str) -> RefreshToken:
        token_hash = hash_token(refresh_token)
        token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

        return token

    @staticmethod
    def find_valid(db: Session, refresh_token: str) -> RefreshToken:
        token_hash = hash_token(refresh_token)
        token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        ).first()

        return token

    @staticmethod
    def revoke(db: Session, token: RefreshToken) -> None:
        token.revoked = True
        db.add(token)
        db.commit()


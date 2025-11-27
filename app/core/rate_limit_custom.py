from datetime import datetime, timedelta, timezone
from sqlalchemy.orm  import Session
from fastapi import HTTPException
from ..models import PasswordResetLog


def too_many_resets_email(db: Session, email: str, minutes: int = 10) -> bool:
    limit_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    count = (
        db.query(PasswordResetLog).filter(
            PasswordResetLog.email == email,
            PasswordResetLog.created_at >= limit_time
        )
        .count()
    )

    return count >= 1    #1 reset every 10 minutes


def too_many_resets_ip(db: Session, ip: str, minutes: int = 10, limit: int = 3) -> bool:
    """Allow only `limit` password reset requests per IP every X minutes."""

    limit_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    count = (
        db.query(PasswordResetLog).filter(
            PasswordResetLog.ip == ip,
            PasswordResetLog.created_at >= limit_time
        )
        .count()
    )

    return count >= limit



def log_reset_attempt(db: Session, email: str, ip: str) -> None:
    entry = PasswordResetLog(email=email, ip=ip)
    db.add(entry)
    db.commit()

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models import LoginAttempt


# Register attempts
def record_login_attempts(db: Session, email: str, ip: str, success: bool) -> None:
    print("Saving login attempt...")
    db.add(LoginAttempt(email=email, ip=ip, success=success))
    db.commit()


# IP failures
def too_many_failures_ip(db: Session, ip: str, max_failures: int = 5, minutes: int = 15) -> bool:
    limit_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    failures = db.query(LoginAttempt).filter(
        LoginAttempt.ip == ip,
        LoginAttempt.success == False,
        LoginAttempt.created_at >= limit_time,
    ).count()

    return failures >= max_failures


# Email failures
def too_many_failures_email(db: Session, email: str, max_failures: int = 5, minutes: int = 15) -> bool:
    limit_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    failures = db.query(LoginAttempt).filter(
        LoginAttempt.email == email,
        LoginAttempt.success == False,
        LoginAttempt.created_at >= limit_time,
    ).count()

    return failures >= max_failures


# Clears errors after successful login
def clear_failures(db: Session, email: str, ip: str) -> None:
    db.query(LoginAttempt).filter(
        (LoginAttempt.email == email) | (LoginAttempt.ip == ip),
    ).delete()
    db.commit()


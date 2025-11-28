# app/core/security_log.py

from sqlalchemy.orm import Session
from fastapi import Request
from typing import Optional
from datetime import datetime, timezone

from app.models import SecurityLog


def log_security_event(
    db: Session,
    action: str,
    status: str,
    detail: str = "",
    request: Optional[Request] = None,
    user_id: Optional[int] = None,
    email: Optional[str] = None,
):
    """
    Creates a detailed security log.
    Can be called in both routes and internal scripts.
    """

    ip = request.client.host if request else "internal"
    path = request.url.path if request else "internal"
    method = request.method if request else "internal"

    log = SecurityLog(
        user_id=user_id,
        email=email,
        action=action,
        ip=ip,
        path=path,
        method=method,
        status_code=status,
        detail=detail,
        created_at=datetime.now(timezone.utc)
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

# app/core/security_log.py

from sqlalchemy.orm import Session
from fastapi import Request

from ..models import SecurityLog


# app/core/security_log.py

from sqlalchemy.orm import Session
from fastapi import Request
from ..models import SecurityLog


def log_security_event(
    db: Session,
    action: str,
    status: str,
    detail: str,
    request: Request,
    user_id: int | None = None,
    email: str | None = None,
):
    log = SecurityLog(
        user_id=user_id,
        email=email,
        action=action,
        ip=request.client.host,
        path=request.url.path,
        method=request.method,
        status_code=status,
        detail=detail,
    )

    db.add(log)
    db.commit()

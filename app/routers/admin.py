from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import SecurityLog, User
from ..schemas import SecurityLogList, SecurityLogEntry
from ..core.permissions import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/security-logs", response_model=SecurityLogList)
def list_security_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),

    email: Optional[str] = None,
    ip: Optional[str] = None,
    action: Optional[str] = None,
    status_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    # USE O MODELO SQLALCHEMY
    query = db.query(SecurityLog)

    # Filters
    if email:
        query = query.filter(SecurityLog.email == email)

    if ip:
        query = query.filter(SecurityLog.ip == ip)

    if action:
        query = query.filter(SecurityLog.action == action)

    if status_code:
        query = query.filter(SecurityLog.status_code == status_code)

    if date_from:
        query = query.filter(SecurityLog.created_at >= date_from)

    if date_to:
        query = query.filter(SecurityLog.created_at <= date_to)

    total = query.count()

    logs = (
        query.order_by(SecurityLog.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # CONVERT SQLAlchemy → Pydantic
    return SecurityLogList(
        total=total,
        page=page,
        limit=limit,
        result=[SecurityLogEntry.model_validate(log) for log in logs]
    )

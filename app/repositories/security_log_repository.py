from sqlalchemy.orm import Session
from typing import List

from app.models import SecurityLog


class SecurityLogRepository:

    @staticmethod
    def create(db: Session, **data: dict) -> SecurityLog:
        log = SecurityLog(**data)
        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    @staticmethod
    def list(db: Session, filters: dict, page: int, limit: int) -> List[SecurityLog]:
        query = db.query(SecurityLog)

        for field, value in filters.items():
            if value:
                query = query.filter(getattr(SecurityLog, field) == value)

        total = query.count()
        logs = query.order_by(SecurityLog.created_at.desc()) \
                    .offset((page - 1) * limit) \
                    .limit(limit) \
                    .all()

        return total, logs

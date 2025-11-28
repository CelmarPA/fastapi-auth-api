from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

from app.database import Base


class PasswordResetLog(Base):
    __tablename__ = "password_reset_logs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    ip = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

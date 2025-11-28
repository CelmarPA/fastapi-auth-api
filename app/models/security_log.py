from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String, index=True, nullable=True)
    action = Column(String, index=True, nullable=False)
    ip = Column(String, index=True, nullable=True)
    path = Column(String, index=True, nullable=False)
    method = Column(String, index=True, nullable=False)
    status_code = Column(String, index=True, nullable=False)  # success / fail
    detail = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", lazy="joined")

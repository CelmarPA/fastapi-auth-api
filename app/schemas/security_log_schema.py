from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List


class SecurityLogEntry(BaseModel):
    id: int
    user_id: Optional[int]
    email: Optional[EmailStr]
    action: str
    ip:  Optional[str]
    path: str
    method: str
    status_code: str
    detail: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecurityLogList(BaseModel):
    total: int
    page: int
    limit: int
    result: List[SecurityLogEntry]

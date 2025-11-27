from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str  # opaque token in text


class Message(BaseModel):
    detail: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetInput(BaseModel):
    token: str
    new_password: str


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

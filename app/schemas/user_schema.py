from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    role: str
    is_active: bool


class UserListItem(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

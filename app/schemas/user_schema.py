from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    role: str
    is_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserListItem(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email: EmailStr
    password: str


class LogoutRequest(BaseModel):
    refresh_token: str
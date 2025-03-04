from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
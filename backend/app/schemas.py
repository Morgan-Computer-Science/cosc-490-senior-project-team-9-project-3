from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


# ---------- User schemas ----------

class UserBase(BaseModel):
    email: EmailStr
    name: str
    major: Optional[str] = None
    year: Optional[str] = None


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # enables ORM mode


# ---------- Token schemas ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(default=None, min_length=2)
    major: Optional[str] = None
    year: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2)
    major: Optional[str] = None
    year: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    credits: Optional[int] = None
    department: Optional[str] = None
    level: Optional[str] = None
    semester_offered: Optional[str] = None
    instructor: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseOut(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ChatSessionCreate(BaseModel):
    title: Optional[str] = None


class ChatSessionOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    sender: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSendResponse(BaseModel):
    user_message: ChatMessageOut
    ai_message: ChatMessageOut

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
        from_attributes = True  


# ---------- Token schemas ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------- Course ----------

class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    credits: Optional[int] = 3
    department: Optional[str] = "Computer Science"
    level: Optional[str] = None          
    semester_offered: Optional[str] = None  


class CourseCreate(CourseBase):
    """Fields required when creating a course."""
    pass


class CourseUpdate(BaseModel):
    """Fields allowed when updating a course (all optional)."""
    code: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    department: Optional[str] = None
    level: Optional[str] = None
    semester_offered: Optional[str] = None


class CourseOut(CourseBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Faculty ----------

class FacultyBase(BaseModel):
    name: str
    title: Optional[str] = None
    email: EmailStr
    office: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = "Computer Science"
    office_hours: Optional[str] = None


class FacultyCreate(FacultyBase):
    """Fields required when creating a faculty member."""
    pass


class FacultyUpdate(BaseModel):
    """Fields allowed when updating a faculty member (all optional)."""
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    office: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    office_hours: Optional[str] = None


class FacultyOut(FacultyBase):
    id: int

    class Config:
        from_attributes = True



# ---------- Chat ----------

class ChatSessionBase(BaseModel):
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionOut(ChatSessionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass  # user sends content; session_id comes from the URL


class ChatMessageOut(ChatMessageBase):
    id: int
    session_id: int
    sender: str
    created_at: datetime

    class Config:
        from_attributes = True
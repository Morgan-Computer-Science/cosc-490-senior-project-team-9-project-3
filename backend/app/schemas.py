from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[str] = None


class UserCreate(UserBase):
    password: str


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


class FacultyBase(BaseModel):
    name: str
    department: Optional[str] = None
    email: Optional[str] = None
    office: Optional[str] = None
    title: Optional[str] = None


class FacultyCreate(FacultyBase):
    pass


class FacultyOut(FacultyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    name: str
    office: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DegreeRequirementBase(BaseModel):
    major: str
    required_courses: Optional[str] = None
    notes: Optional[str] = None


class DegreeRequirementCreate(DegreeRequirementBase):
    pass


class DegreeRequirementOut(DegreeRequirementBase):
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
    content: str


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
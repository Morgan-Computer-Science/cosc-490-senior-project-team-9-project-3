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


class CompletedCourseOut(BaseModel):
    id: int
    course_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompletedCoursesUpdate(BaseModel):
    course_codes: list[str] = Field(default_factory=list)


class CompletedCoursesImportPreview(BaseModel):
    import_source: str = "manual"
    detected_document_type: str = "text_document"
    extraction_method: str = "text_local"
    summary: Optional[str] = None
    confidence_note: Optional[str] = None
    matched_course_codes: list[str] = Field(default_factory=list)
    completed_course_codes: list[str] = Field(default_factory=list)
    planned_course_codes: list[str] = Field(default_factory=list)
    remaining_course_codes: list[str] = Field(default_factory=list)
    unknown_course_codes: list[str] = Field(default_factory=list)
    matched_count: int = 0
    source_summary: Optional[str] = None


class ConnectorSummary(BaseModel):
    id: str
    display_name: str
    status: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    supports_file_upload: bool = False
    requires_authentication: bool = False
    launch_stage: str


class ConnectorDetail(ConnectorSummary):
    supported_record_types: list[str] = Field(default_factory=list)


class NormalizedAcademicRecord(BaseModel):
    connector_id: str
    source_type: str
    record_type: str
    confidence: Optional[str] = None
    raw_summary: Optional[str] = None
    course_codes: list[str] = Field(default_factory=list)
    detected_document_type: Optional[str] = None


class DegreeProgressSummary(BaseModel):
    major: Optional[str] = None
    required_courses: list[str] = Field(default_factory=list)
    completed_courses: list[str] = Field(default_factory=list)
    remaining_courses: list[str] = Field(default_factory=list)
    recommended_next_courses: list[str] = Field(default_factory=list)
    blocked_courses: list[str] = Field(default_factory=list)
    completion_percent: float = 0.0
    notes: Optional[str] = None
    advising_tips: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    completed_courses: list[CompletedCourseOut] = Field(default_factory=list)

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


class DepartmentInfo(BaseModel):
    department: str
    major: Optional[str] = None
    office: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    overview: Optional[str] = None
    school: Optional[str] = None
    source_url: Optional[str] = None


class ProgramInfo(BaseModel):
    major: str
    canonical_major: Optional[str] = None
    degree_type: Optional[str] = None
    department: Optional[str] = None
    school: Optional[str] = None
    aliases: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class FacultyInfo(BaseModel):
    name: str
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    office: Optional[str] = None
    office_hours: Optional[str] = None
    specialties: Optional[str] = None


class SupportResourceInfo(BaseModel):
    resource: str
    category: Optional[str] = None
    contact: Optional[str] = None
    details: Optional[str] = None


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


class AdvisorInsights(BaseModel):
    intent: str
    emotional_tone: str
    needs_support: bool = False
    matched_signals: list[str] = Field(default_factory=list)
    recommended_next_courses: list[str] = Field(default_factory=list)
    blocked_courses: list[str] = Field(default_factory=list)
    suggested_contacts: list[str] = Field(default_factory=list)
    retrieved_sources: list[str] = Field(default_factory=list)
    attachment_summary: Optional[str] = None


class ChatSendResponse(BaseModel):
    user_message: ChatMessageOut
    ai_message: ChatMessageOut
    advisor_insights: AdvisorInsights

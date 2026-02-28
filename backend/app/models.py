from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    major = Column(String, nullable=True)
    year = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat_sessions = relationship("ChatSession", back_populates="user")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)  
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, default=3)
    department = Column(String, default="Computer Science")
    level = Column(String, nullable=True)  
    semester_offered = Column(String, nullable=True)  


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    office = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, default="Computer Science")
    office_hours = Column(String, nullable=True)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  
    content = Column(Text, nullable=False)
    emotion = Column(String, nullable=True)  # "positive", "negative", "neutral"
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class CurriculumUpdate(Base):
    __tablename__ = "curriculum_updates"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, nullable=False)  # matches Course.code
    update_type = Column(String, nullable=False)  # "prerequisite-change"
    description = Column(Text, nullable=True)
    effective_date = Column(String, nullable=True)  # store as string for now
    created_at = Column(DateTime, default=datetime.utcnow)
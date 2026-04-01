import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas
from .ai_client import generate_ai_reply
from .auth import get_current_user
from .db import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_course_context(db: Session, question: str, limit: int = 8) -> str:
    terms = re.findall(r"[A-Za-z0-9]+", question)
    if not terms:
        return ""

    filters = []
    for term in terms:
        like = f"%{term}%"
        filters.extend(
            [
                models.Course.code.ilike(like),
                models.Course.title.ilike(like),
                models.Course.description.ilike(like),
                models.Course.department.ilike(like),
                models.Course.instructor.ilike(like),
            ]
        )

    courses = db.query(models.Course).filter(or_(*filters)).limit(limit).all()
    if not courses:
        return ""

    lines = ["Relevant Morgan State course context:"]
    for course in courses:
        details = []
        if course.credits is not None:
            details.append(f"{course.credits} credits")
        if course.department:
            details.append(f"Department: {course.department}")
        if course.level:
            details.append(f"Level: {course.level}")
        if course.semester_offered:
            details.append(f"Offered: {course.semester_offered}")
        if course.instructor:
            details.append(f"Instructor: {course.instructor}")

        header = f"- {course.code}: {course.title}"
        if details:
            header += f" ({', '.join(details)})"

        lines.append(header)
        if course.description:
            lines.append(f"  Description: {course.description}")

    return "\n".join(lines)


def _build_student_context(user: models.User) -> str:
    pieces = ["Student profile context:"]
    pieces.append(f"- Name: {user.full_name or 'Not provided'}")
    pieces.append(f"- Major: {user.major or 'Undeclared'}")
    pieces.append(f"- Year: {user.year or 'Not provided'}")
    return "\n".join(pieces)


def _fallback_advising_reply(user: models.User, question: str, course_context: str) -> str:
    lines = [
        f"I could not reach the live AI service, but I can still help with grounded Morgan State info for a {user.year or 'current'} {user.major or 'student'}.",
    ]

    if course_context:
        context_lines = [line.strip() for line in course_context.splitlines() if line.strip()]
        relevant = [line for line in context_lines if line.startswith("- ")][:3]
        if relevant:
            lines.append("Relevant catalog matches:")
            lines.extend(line.replace("- ", "- ", 1) for line in relevant)

    lowered = question.lower()
    if "after" in lowered or "next" in lowered or "plan" in lowered:
        lines.append(
            "For planning questions, compare the matched course levels, semester offerings, and any known prerequisites before locking a schedule."
        )

    lines.append(
        "If you want a final degree-plan decision, check with the Computer Science department or your assigned advisor."
    )
    return "\n".join(lines)


def _get_user_session(db: Session, user_id: int, session_id: int) -> models.ChatSession:
    session = (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == user_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return session


@router.post("/sessions", response_model=schemas.ChatSessionOut)
def create_chat_session(
    data: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = models.ChatSession(
        user_id=current_user.id,
        title=(data.title or "New advising session").strip(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[schemas.ChatSessionOut])
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == current_user.id)
        .order_by(models.ChatSession.created_at.desc(), models.ChatSession.id.desc())
        .all()
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)
    db.delete(session)
    db.commit()


@router.get("/sessions/{session_id}/messages", response_model=List[schemas.ChatMessageOut])
def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc(), models.ChatMessage.id.asc())
        .all()
    )


@router.post("/sessions/{session_id}/messages", response_model=schemas.ChatSendResponse)
def send_message(
    session_id: int,
    data: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)
    clean_content = data.content.strip()

    user_msg = models.ChatMessage(
        session_id=session.id,
        sender="user",
        content=clean_content,
    )
    db.add(user_msg)
    db.flush()

    history = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc(), models.ChatMessage.id.asc())
        .all()
    )

    if session.title == "New advising session" and clean_content:
        session.title = clean_content[:40]

    history_payload = [
        {
            "role": "assistant" if message.sender == "assistant" else "user",
            "content": message.content,
        }
        for message in history[-12:]
    ]

    course_context = _build_course_context(db, clean_content)
    student_context = _build_student_context(current_user)
    extra_context = "\n\n".join(part for part in [student_context, course_context] if part)

    try:
        ai_text = generate_ai_reply(history=history_payload, extra_context=extra_context)
    except Exception as exc:
        print("AI error in generate_ai_reply:", repr(exc))
        ai_text = _fallback_advising_reply(current_user, clean_content, course_context)

    ai_msg = models.ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_text,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(ai_msg)

    return schemas.ChatSendResponse(user_message=user_msg, ai_message=ai_msg)

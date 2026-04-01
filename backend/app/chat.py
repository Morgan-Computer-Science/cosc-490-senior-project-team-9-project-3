from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .ai_client import generate_ai_reply
from .auth import get_current_user
from .db import get_db
from .rag import (
    RetrievedDocument,
    format_retrieved_context,
    get_degree_progress,
    retrieve_relevant_documents,
)

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_student_context(user: models.User) -> str:
    pieces = ["Student profile context:"]
    pieces.append(f"- Name: {user.full_name or 'Not provided'}")
    pieces.append(f"- Major: {user.major or 'Undeclared'}")
    pieces.append(f"- Year: {user.year or 'Not provided'}")
    completed_codes = [course.course_code for course in user.completed_courses]
    if completed_codes:
        pieces.append(f"- Completed Courses: {', '.join(sorted(completed_codes))}")
    return "\n".join(pieces)


def _build_degree_progress_context(user: models.User) -> str:
    summary = get_degree_progress(
        user.major,
        [course.course_code for course in user.completed_courses],
    )
    if not summary["required_courses"]:
        return ""

    lines = ["Degree progress context:"]
    lines.append(f"- Major: {summary['major']}")
    lines.append(f"- Completion: {summary['completion_percent']}%")
    lines.append(
        f"- Remaining Required Courses: {', '.join(summary['remaining_courses']) or 'None listed'}"
    )
    if summary["recommended_next_courses"]:
        lines.append(
            f"- Recommended Next Courses: {', '.join(summary['recommended_next_courses'])}"
        )
    if summary["notes"]:
        lines.append(f"- Notes: {summary['notes']}")
    if summary["advising_tips"]:
        lines.append(f"- Advising Tips: {summary['advising_tips']}")
    return "\n".join(lines)


def _fallback_advising_reply(
    user: models.User,
    question: str,
    documents: List[RetrievedDocument],
) -> str:
    relevant = documents[:3]
    lines = [
        f"I could not reach the live AI service, but I can still help with grounded Morgan State info for a {user.year or 'current'} {user.major or 'student'}.",
    ]

    if relevant:
        lines.append("Most relevant retrieved information:")
        for doc in relevant:
            lines.append(f"- {doc.title}")
            lines.append(f"  {doc.content}")
            if doc.contact:
                lines.append(f"  Contact: {doc.contact}")

    lowered = question.lower()
    if not documents:
        lines.append(
            "I do not yet have enough Morgan State source material for that question, so I would not want to guess."
        )

    if "after" in lowered or "next" in lowered or "plan" in lowered:
        lines.append(
            "For planning questions, compare required courses, course levels, semester offerings, and department guidance before locking a schedule."
        )

    if any(token in lowered for token in ["stress", "anxious", "overwhelmed", "mental", "counseling"]):
        lines.append(
            "If the concern is also personal or wellness-related, the Counseling Center or University Advising may be a better immediate support contact."
        )

    contacts = [doc.contact for doc in documents if doc.contact]
    if contacts:
        lines.append(f"Best next contact from the retrieved context: {contacts[0]}")
    else:
        lines.append(
            "If you need a final policy or degree decision, check with University Advising or the department that owns your major."
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

    retrieved_docs = retrieve_relevant_documents(
        clean_content,
        user_major=current_user.major,
        top_k=6,
    )
    retrieved_context = format_retrieved_context(retrieved_docs)
    student_context = _build_student_context(current_user)
    degree_progress_context = _build_degree_progress_context(current_user)
    extra_context = "\n\n".join(
        part for part in [student_context, degree_progress_context, retrieved_context] if part
    )

    try:
        ai_text = generate_ai_reply(history=history_payload, extra_context=extra_context)
    except Exception as exc:
        print("AI error in generate_ai_reply:", repr(exc))
        ai_text = _fallback_advising_reply(current_user, clean_content, retrieved_docs)

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

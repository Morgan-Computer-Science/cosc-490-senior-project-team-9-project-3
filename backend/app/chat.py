from typing import List
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from . import models, schemas
from .db import get_db
from .auth import get_current_user
from .ai_client import generate_ai_reply

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# ---------- Helpers ----------


def _build_course_context(db: Session, question: str, limit: int = 8) -> str:
    """
    Very simple keyword search over courses to give Gemini real data.
    Looks in code, title, description, and department.
    """
    terms = re.findall(r"[A-Za-z0-9]+", question)
    if not terms:
        return ""

    query = db.query(models.Course)

    filters = []
    for term in terms:
        like = f"%{term}%"
        filters.extend(
            [
                models.Course.code.ilike(like),
                models.Course.title.ilike(like),
                models.Course.description.ilike(like),
                models.Course.department.ilike(like),
            ]
        )

    query = query.filter(or_(*filters)).limit(limit)
    courses = query.all()

    if not courses:
        return ""

    lines = ["Morgan State course catalog entries that may be relevant:"]
    for c in courses:
        line = f"- {c.code}: {c.title}"
        details = []

        if c.credits is not None:
            details.append(f"{c.credits} credits")
        if c.department:
            details.append(f"Dept: {c.department}")
        if c.semester_offered:
            details.append(f"Offered: {c.semester_offered}")

        if details:
            line += " (" + ", ".join(details) + ")"

        lines.append(line)

        if c.description:
            lines.append(f"  Description: {c.description}")

    return "\n".join(lines)


def _get_user_session(
    db: Session,
    user_id: int,
    session_id: int,
) -> models.ChatSession:
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


# ---------- Sessions ----------


@router.post("/sessions", response_model=schemas.ChatSessionOut)
def create_chat_session(
    data: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    title = data.title or "New advising session"

    session = models.ChatSession(
        user_id=current_user.id,
        title=title,
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
        .order_by(models.ChatSession.created_at.desc())
        .all()
    )


# ---------- Messages ----------


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[schemas.ChatMessageOut],
)
def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)
    # return messages sorted oldest → newest
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=schemas.ChatSendResponse,
)
def send_message(
    session_id: int,
    data: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)

    # Save the user's message
    user_msg = models.ChatMessage(
        session_id=session.id,
        sender="user",
        content=data.content,
    )
    db.add(user_msg)
    db.flush()  # get user_msg.id without committing yet

    #Load conversation history (oldest → newest)
    history = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc(), models.ChatMessage.id.asc())
        .all()
    )

    history_payload = []
    for m in history:
        role = "assistant" if m.sender == "assistant" else "user"
        history_payload.append(
            {
                "role": role,
                "content": m.content,
            }
        )

    #Build catalog context from the user's latest question
    course_context = _build_course_context(db, data.content)

    #Generate AI response using history + course catalog context
    try:
        ai_text = generate_ai_reply(
            history=history_payload,
            extra_context=course_context,
        )
    except Exception as e:
        print("AI error in generate_ai_reply:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI response: {e}",
        )
        ai_text = (
            "I'm sorry, I couldn't generate a response right now. "
            "Please contact your advisor or try again later."
        )

    # Save AI's message
    ai_msg = models.ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_text,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(ai_msg)

    return schemas.ChatSendResponse(
        user_message=user_msg,
        ai_message=ai_msg,
    )
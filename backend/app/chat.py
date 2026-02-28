from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


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
    # basic default title if user doesn't pass one in
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
    # just return messages sorted oldest → newest
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=schemas.ChatMessageOut,
)
def send_message(
    session_id: int,
    data: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)

    # for now we just save the user message;
    # AI response will be hooked in later
    msg = models.ChatMessage(
        session_id=session.id,
        sender="user",
        content=data.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
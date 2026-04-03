from typing import List
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from . import models, schemas
from .attachments import extract_attachment_context
from .ai_client import generate_ai_reply
from .auth import get_current_user
from .db import get_db
from .rag import (
    AttachmentCourseSignals,
    RetrievedDocument,
    compare_degree_audit,
    evaluate_course_plan,
    extract_attachment_course_signals,
    extract_known_course_codes,
    format_retrieved_context,
    get_course_documents_by_code,
    get_degree_progress,
    retrieve_relevant_documents,
    summarize_schedule_plan,
)
from .student_state import analyze_student_state

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_student_context(user: models.User, effective_completed_codes: list[str] | None = None) -> str:
    pieces = ["Student profile context:"]
    pieces.append(f"- Name: {user.full_name or 'Not provided'}")
    pieces.append(f"- Major: {user.major or 'Undeclared'}")
    pieces.append(f"- Year: {user.year or 'Not provided'}")
    completed_codes = effective_completed_codes or [course.course_code for course in user.completed_courses]
    if completed_codes:
        pieces.append(f"- Completed Courses: {', '.join(sorted(completed_codes))}")
    return "\n".join(pieces)


def _build_degree_progress_context(
    user: models.User,
    effective_completed_codes: list[str] | None = None,
) -> str:
    summary = get_degree_progress(
        user.major,
        effective_completed_codes or [course.course_code for course in user.completed_courses],
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
    if summary["blocked_courses"]:
        lines.append(
            f"- Courses Still Blocked By Prerequisites: {', '.join(summary['blocked_courses'][:6])}"
        )
    if summary["notes"]:
        lines.append(f"- Notes: {summary['notes']}")
    if summary["advising_tips"]:
        lines.append(f"- Advising Tips: {summary['advising_tips']}")
    return "\n".join(lines)


def _build_advisor_insights(
    user: models.User,
    student_state: dict[str, object],
    retrieved_docs: List[RetrievedDocument],
    attachment_summary: str | None = None,
    effective_completed_codes: list[str] | None = None,
) -> schemas.AdvisorInsights:
    degree_progress = get_degree_progress(
        user.major,
        effective_completed_codes or [course.course_code for course in user.completed_courses],
    )
    contact_candidates: list[str] = []
    source_titles: list[str] = []
    for doc in retrieved_docs[:4]:
        source_titles.append(doc.title)
        if doc.contact and doc.contact not in contact_candidates:
            contact_candidates.append(doc.contact)

    return schemas.AdvisorInsights(
        intent=str(student_state["intent"]),
        emotional_tone=str(student_state["emotional_tone"]),
        needs_support=bool(student_state["needs_support"]),
        matched_signals=[str(signal) for signal in student_state.get("matched_signals", [])],
        recommended_next_courses=[
            str(code) for code in degree_progress.get("recommended_next_courses", [])[:4]
        ],
        blocked_courses=[str(code) for code in degree_progress.get("blocked_courses", [])[:4]],
        suggested_contacts=contact_candidates[:3],
        retrieved_sources=source_titles,
        attachment_summary=attachment_summary,
    )


def _build_student_state_context(question: str, user: models.User) -> tuple[str, dict[str, object]]:
    state = analyze_student_state(question, major=user.major)
    lines = ["Student state analysis:"]
    lines.append(f"- Intent: {state['intent']}")
    lines.append(f"- Emotional Tone: {state['emotional_tone']}")
    lines.append(f"- Needs Support Escalation: {'yes' if state['needs_support'] else 'no'}")
    if state["matched_signals"]:
        lines.append(f"- Matched Signals: {', '.join(state['matched_signals'])}")
    return "\n".join(lines), state


def _merge_retrieved_documents(*groups: List[RetrievedDocument]) -> list[RetrievedDocument]:
    merged: list[RetrievedDocument] = []
    seen: set[tuple[str, str]] = set()
    for group in groups:
        for doc in group:
            key = (doc.source_type, doc.title)
            if key in seen:
                continue
            seen.add(key)
            merged.append(doc)
    return merged


def _build_attachment_course_context(attachment_context) -> tuple[str, list[RetrievedDocument]]:
    if not attachment_context or not attachment_context.extracted_text:
        return "", []

    matched_codes = extract_known_course_codes(attachment_context.extracted_text)
    if not matched_codes:
        return "", []

    matched_docs = get_course_documents_by_code(matched_codes, limit=6)
    lines = [
        "Attachment-derived advising evidence:",
        (
            f"- Possible Morgan course codes recognized in the uploaded "
            f"{attachment_context.document_type.replace('_', ' ')}: {', '.join(matched_codes)}"
        ),
    ]
    if matched_docs:
        lines.append(format_retrieved_context(matched_docs))
    return "\n".join(lines), matched_docs


def _build_attachment_signal_context(
    attachment_context,
    attachment_signals: AttachmentCourseSignals,
    user: models.User,
    effective_completed_codes: list[str],
) -> str:
    if not attachment_context:
        return ""

    lines: list[str] = []
    if attachment_signals.completed_codes:
        lines.append(
            f"- Recognized completed courses from the uploaded {attachment_context.document_type.replace('_', ' ')}: "
            f"{', '.join(attachment_signals.completed_codes)}"
        )
    if attachment_signals.remaining_codes:
        lines.append(
            f"- Recognized remaining or needed courses from the uploaded {attachment_context.document_type.replace('_', ' ')}: "
            f"{', '.join(attachment_signals.remaining_codes)}"
        )
        if attachment_context.document_type == "degree_audit":
            audit_comparison = compare_degree_audit(
                attachment_signals.remaining_codes,
                effective_completed_codes,
                user.major,
            )
            if audit_comparison["overlap_remaining"]:
                lines.append(
                    f"- Remaining courses that match the app's current degree-progress view: "
                    f"{', '.join(audit_comparison['overlap_remaining'])}"
                )
            if audit_comparison["audit_only_remaining"]:
                lines.append(
                    f"- Remaining courses listed by the uploaded audit but not currently in the app's remaining-course set: "
                    f"{', '.join(audit_comparison['audit_only_remaining'])}"
                )
            if audit_comparison["system_only_remaining"]:
                lines.append(
                    f"- Courses the app still expects as remaining that were not clearly recognized in the uploaded audit: "
                    f"{', '.join(audit_comparison['system_only_remaining'][:8])}"
                )
    if attachment_signals.planned_codes:
        schedule_evaluation = evaluate_course_plan(
            attachment_signals.planned_codes,
            effective_completed_codes,
        )
        schedule_summary = summarize_schedule_plan(
            attachment_signals.planned_codes,
            effective_completed_codes,
            user.major,
        )
        lines.append(
            f"- Recognized planned or scheduled courses from the uploaded {attachment_context.document_type.replace('_', ' ')}: "
            f"{', '.join(attachment_signals.planned_codes)}"
        )
        if schedule_summary["total_credits"] is not None:
            lines.append(
                f"- Estimated total credits in the planned schedule: {schedule_summary['total_credits']}"
            )
        if schedule_evaluation["ready_courses"]:
            lines.append(
                f"- Planned courses that look ready based on known prerequisites: "
                f"{', '.join(schedule_evaluation['ready_courses'])}"
            )
        if schedule_evaluation["blocked_courses"]:
            lines.append(
                f"- Planned courses that may be blocked by prerequisites: "
                f"{'; '.join(schedule_evaluation['blocked_courses'])}"
            )
        if schedule_evaluation["already_completed_courses"]:
            lines.append(
                f"- Planned courses that already appear completed: "
                f"{', '.join(schedule_evaluation['already_completed_courses'])}"
            )
        if schedule_summary["required_in_plan"]:
            lines.append(
                f"- Planned courses that match known required courses for the student's major: "
                f"{', '.join(schedule_summary['required_in_plan'])}"
            )
        if schedule_summary["outside_known_requirements"]:
            lines.append(
                f"- Planned courses not currently listed in the known required-course set for the student's major: "
                f"{', '.join(schedule_summary['outside_known_requirements'])}"
            )

    if not lines:
        return ""

    return "Attachment planning signals:\n" + "\n".join(lines)


def _fallback_advising_reply(
    user: models.User,
    question: str,
    documents: List[RetrievedDocument],
    student_state: dict[str, object],
    ) -> str:
    relevant = documents[:3]
    opening = (
        f"I could not reach the live AI service, but I can still help with grounded Morgan State info for a {user.year or 'current'} {user.major or 'student'}."
    )
    if student_state["needs_support"]:
        opening = (
            "I could not reach the live AI service, but I do want to respond carefully. "
            "It sounds like this may involve stress or personal support as well as academics."
        )
    lines = [opening]

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

    if student_state["needs_support"] or any(token in lowered for token in ["stress", "anxious", "overwhelmed", "mental", "counseling"]):
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


def _infer_completed_courses_from_attachment(attachment_context) -> list[str]:
    if not attachment_context or not attachment_context.extracted_text:
        return []
    if attachment_context.document_type not in {"transcript", "degree_audit"}:
        return []
    attachment_signals = extract_attachment_course_signals(
        attachment_context.extracted_text,
        attachment_context.document_type,
        limit=20,
    )
    return list(attachment_signals.completed_codes)


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
async def send_message(
    session_id: int,
    content: str = Form(...),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = _get_user_session(db, current_user.id, session_id)
    clean_content = content.strip()
    attachment_context = None
    if attachment:
        attachment_context = await extract_attachment_context(attachment)

    user_msg = models.ChatMessage(
        session_id=session.id,
        sender="user",
        content=clean_content if not attachment_context else f"{clean_content}\n\nAttachment: {attachment_context.filename}",
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
    attachment_course_context, attachment_course_docs = _build_attachment_course_context(
        attachment_context
    )
    attachment_signals = extract_attachment_course_signals(
        attachment_context.extracted_text if attachment_context else None,
        attachment_context.document_type if attachment_context else None,
    )
    inferred_completed_codes = _infer_completed_courses_from_attachment(attachment_context)
    effective_completed_codes = sorted(
        {
            *[course.course_code for course in current_user.completed_courses],
            *inferred_completed_codes,
        }
    )
    attachment_signal_context = _build_attachment_signal_context(
        attachment_context,
        attachment_signals,
        current_user,
        effective_completed_codes,
    )
    combined_docs = _merge_retrieved_documents(retrieved_docs, attachment_course_docs)
    retrieved_context = format_retrieved_context(combined_docs)
    student_context = _build_student_context(current_user, effective_completed_codes)
    degree_progress_context = _build_degree_progress_context(current_user, effective_completed_codes)
    student_state_context, student_state = _build_student_state_context(clean_content, current_user)
    advisor_insights = _build_advisor_insights(
        current_user,
        student_state,
        combined_docs,
        attachment_context.summary if attachment_context else None,
        effective_completed_codes,
    )
    extra_context = "\n\n".join(
        part
        for part in [
            student_context,
            degree_progress_context,
            student_state_context,
            attachment_context.context_text if attachment_context else "",
            attachment_course_context,
            attachment_signal_context,
            retrieved_context,
        ]
        if part
    )

    try:
        ai_text = generate_ai_reply(
            history=history_payload,
            extra_context=extra_context,
            attachment_path=attachment_context.temp_path if attachment_context else None,
            attachment_mime_type=attachment_context.content_type if attachment_context else None,
            attachment_summary=attachment_context.summary if attachment_context else None,
            attachment_document_type=attachment_context.document_type if attachment_context else None,
        )
    except Exception as exc:
        print("AI error in generate_ai_reply:", repr(exc))
        ai_text = _fallback_advising_reply(current_user, clean_content, combined_docs, student_state)
    finally:
        if attachment_context and attachment_context.temp_path:
            try:
                os.remove(attachment_context.temp_path)
            except OSError:
                pass

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
        advisor_insights=advisor_insights,
    )

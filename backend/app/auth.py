from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, security
from .attachments import extract_attachment_context
from .db import get_db
from .rag import (
    extract_all_course_codes,
    extract_attachment_course_signals,
    extract_known_course_codes,
    get_degree_progress,
    load_course_rows,
)
from .rate_limit import limit_auth, limit_import

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    request: Request,
    _: None = Depends(limit_auth),
    db: Session = Depends(get_db),
):
    existing = _get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    new_user = models.User(
        email=user_in.email,
        hashed_password=security.hash_password(user_in.password),
        full_name=user_in.full_name,
        major=user_in.major,
        year=user_in.year,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(
    request: Request,
    _: None = Depends(limit_auth),
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = _get_user_by_email(db, form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return schemas.Token(access_token=access_token)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    payload = security.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(models.User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def _serialize_user(user: models.User) -> schemas.UserRead:
    return schemas.UserRead.model_validate(user)


def _normalize_import_source(import_source: str) -> str:
    allowed = {"manual", "transcript_text", "canvas_export", "websis_export"}
    normalized = (import_source or "manual").strip().lower()
    return normalized if normalized in allowed else "manual"


def _infer_import_document_type(import_source: str, attachment_context, import_text: str = "") -> str:
    if attachment_context and attachment_context.document_type:
        return attachment_context.document_type
    lowered = (import_text or "").lower()
    if import_source == "canvas_export":
        if any(keyword in lowered for keyword in {"current", "enrolled", "semester", "assignment", "dashboard"}):
            return "schedule"
    if import_source == "websis_export":
        if any(
            keyword in lowered
            for keyword in {
                "remaining requirement",
                "remaining requirements",
                "degree audit",
                "program audit",
                "academic record",
                "major:",
            }
        ):
            return "degree_audit"
    if import_source in {"transcript_text", "canvas_export", "websis_export"}:
        return "transcript"
    return "text_document"


def _apply_canvas_import_bias(
    import_text: str,
    completed: list[str],
    planned: list[str],
    remaining: list[str],
) -> tuple[list[str], list[str], list[str]]:
    mentioned = extract_known_course_codes(import_text, limit=30)
    return [], sorted({*planned, *mentioned}), remaining


def _apply_websis_import_bias(
    import_text: str,
    document_type: str,
    completed: list[str],
    planned: list[str],
    remaining: list[str],
) -> tuple[list[str], list[str], list[str]]:
    mentioned = extract_known_course_codes(import_text, limit=30)
    if document_type == "degree_audit":
        if not remaining:
            remaining = sorted(set(mentioned) - set(completed))
        return sorted(set(completed)), planned, sorted(set(remaining))
    if not completed:
        completed = sorted(set(mentioned))
    return completed, planned, remaining


def _build_import_preview_codes(
    import_text: str,
    import_source: str,
    attachment_context,
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    document_type = _infer_import_document_type(import_source, attachment_context, import_text)
    signals = extract_attachment_course_signals(import_text, document_type, limit=30)

    completed = list(signals.completed_codes)
    planned = list(signals.planned_codes)
    remaining = list(signals.remaining_codes)
    mentioned = extract_known_course_codes(import_text, limit=30)

    if import_source == "canvas_export":
        completed, planned, remaining = _apply_canvas_import_bias(
            import_text,
            completed,
            planned,
            remaining,
        )
    elif import_source == "websis_export":
        completed, planned, remaining = _apply_websis_import_bias(
            import_text,
            document_type,
            completed,
            planned,
            remaining,
        )

    if document_type == "degree_audit" and not completed:
        completed = []
    elif (
        import_source != "canvas_export"
        and document_type in {"transcript", "schedule"}
        and not completed
    ):
        completed = list(signals.mentioned_codes)

    combined_candidates = sorted(
        {
            *completed,
            *planned,
            *remaining,
            *mentioned,
        }
    )
    return document_type, combined_candidates, completed, planned, remaining


def _build_import_preview_summary(
    import_source: str,
    detected_document_type: str,
    completed_codes: list[str],
    planned_codes: list[str],
    remaining_codes: list[str],
    matched_codes: list[str],
) -> str:
    document_label = detected_document_type.replace("_", " ")
    if import_source == "canvas_export" and planned_codes:
        return (
            f"This Canvas export looks like current-course context with "
            f"{len(planned_codes)} planned or active course signal"
            f"{'' if len(planned_codes) == 1 else 's'}."
        )
    if import_source == "websis_export" and completed_codes:
        return (
            f"This WebSIS export looks like official course history with "
            f"{len(completed_codes)} completed course"
            f"{'' if len(completed_codes) == 1 else 's'} recognized."
        )
    if completed_codes:
        return (
            f"Recognized {len(completed_codes)} completed course"
            f"{'' if len(completed_codes) == 1 else 's'} from this {document_label}."
        )
    if planned_codes:
        return (
            f"This {document_label} looks like a planning document with "
            f"{len(planned_codes)} planned or current course signal"
            f"{'' if len(planned_codes) == 1 else 's'}."
        )
    if remaining_codes:
        return (
            f"This {document_label} appears to emphasize remaining or needed coursework."
        )
    if matched_codes:
        return (
            f"Recognized {len(matched_codes)} Morgan course code"
            f"{'' if len(matched_codes) == 1 else 's'} in this {document_label}."
        )
    return f"Processed this {document_label}, but no supported Morgan course codes were recognized."


def _build_import_confidence_note(
    import_source: str,
    attachment_context,
) -> str:
    if attachment_context and attachment_context.confidence_note:
        return attachment_context.confidence_note
    if import_source == "canvas_export":
        return (
            "Interpreting this as current-course context from a Canvas-style export, "
            "so active and planned classes are weighted more heavily than completed history."
        )
    if import_source == "websis_export":
        return (
            "Interpreting this as a WebSIS-style academic record export, so completed "
            "and remaining requirement signals are weighted more heavily."
        )
    return "Using the provided text directly for OCR-free course extraction."


@router.get("/me", response_model=schemas.UserRead)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return _serialize_user(current_user)


@router.put("/me", response_model=schemas.UserRead)
def update_current_user(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return _serialize_user(current_user)


@router.put("/me/completed-courses", response_model=list[schemas.CompletedCourseOut])
def update_completed_courses(
    payload: schemas.CompletedCoursesUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    normalized_codes = sorted(
        {
            course_code.strip().upper()
            for course_code in payload.course_codes
            if course_code.strip()
        }
    )

    db.query(models.UserCompletedCourse).filter(
        models.UserCompletedCourse.user_id == current_user.id
    ).delete()

    for course_code in normalized_codes:
        db.add(
            models.UserCompletedCourse(
                user_id=current_user.id,
                course_code=course_code,
            )
        )

    db.commit()
    db.refresh(current_user)
    return current_user.completed_courses


@router.post("/me/completed-courses/import", response_model=schemas.CompletedCoursesImportPreview)
async def import_completed_courses_preview(
    request: Request,
    _: None = Depends(limit_import),
    import_source: str = Form(default="manual"),
    source_text: str = Form(default=""),
    attachment: UploadFile | None = File(default=None),
    current_user: models.User = Depends(get_current_user),
):
    normalized_import_source = _normalize_import_source(import_source)
    attachment_context = await extract_attachment_context(attachment) if attachment else None
    import_text = "\n".join(
        part
        for part in [
            source_text.strip(),
            (attachment_context.extracted_text or "").strip() if attachment_context else "",
        ]
        if part
    ).strip()

    if not import_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide pasted text or upload a file to import completed courses.",
        )

    known_codes = {
        row.get("code", "").strip().upper()
        for row in load_course_rows()
        if row.get("code")
    }
    (
        detected_document_type,
        candidates,
        completed_codes,
        planned_codes,
        remaining_codes,
    ) = _build_import_preview_codes(
        import_text,
        normalized_import_source,
        attachment_context,
    )
    all_detected_codes = set(extract_all_course_codes(import_text, limit=60))
    if attachment_context:
        all_detected_codes.update(attachment_context.signals.unknown_course_codes)
        all_detected_codes.update(attachment_context.signals.matched_course_codes)
    matched = sorted(code for code in candidates if code in known_codes)
    unknown = sorted(code for code in all_detected_codes if code not in known_codes)

    source_labels = {
        "manual": "Manual course import",
        "transcript_text": "Transcript text import",
        "canvas_export": "Canvas-style export import",
        "websis_export": "WebSIS-style export import",
    }
    source_summary = source_labels[normalized_import_source]
    if attachment_context:
        source_summary = f"{source_labels[normalized_import_source]} from {attachment_context.filename}"
    elif current_user.email:
        source_summary = f"{source_labels[normalized_import_source]} for {current_user.email}"

    return schemas.CompletedCoursesImportPreview(
        import_source=normalized_import_source,
        detected_document_type=detected_document_type,
        extraction_method=(
            attachment_context.extraction_method if attachment_context else "text_local"
        ),
        summary=(
            attachment_context.summary
            if attachment_context and attachment_context.summary
            else _build_import_preview_summary(
                normalized_import_source,
                detected_document_type,
                [code for code in completed_codes if code in known_codes],
                [code for code in planned_codes if code in known_codes],
                [code for code in remaining_codes if code in known_codes],
                matched,
            )
        ),
        confidence_note=_build_import_confidence_note(
            normalized_import_source,
            attachment_context,
        ),
        matched_course_codes=matched,
        completed_course_codes=[code for code in completed_codes if code in known_codes],
        planned_course_codes=[code for code in planned_codes if code in known_codes],
        remaining_course_codes=[code for code in remaining_codes if code in known_codes],
        unknown_course_codes=unknown,
        matched_count=len(matched),
        source_summary=source_summary,
    )


@router.get("/me/degree-progress", response_model=schemas.DegreeProgressSummary)
def get_current_user_degree_progress(
    current_user: models.User = Depends(get_current_user),
):
    completed_codes = [course.course_code for course in current_user.completed_courses]
    return schemas.DegreeProgressSummary(
        **get_degree_progress(current_user.major, completed_codes)
    )

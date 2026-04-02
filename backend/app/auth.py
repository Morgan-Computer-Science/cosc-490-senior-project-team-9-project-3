from datetime import timedelta
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, security
from .attachments import extract_attachment_context
from .db import get_db
from .rag import get_degree_progress, load_course_rows

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
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


def _extract_course_code_candidates(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-Z]{2,5}[-\s]?\d{3}\b", text.upper())
    normalized = []
    for candidate in candidates:
        code = re.sub(r"[^A-Z0-9]", "", candidate)
        if code and code not in normalized:
            normalized.append(code)
    return normalized


def _normalize_import_source(import_source: str) -> str:
    allowed = {"manual", "transcript_text", "canvas_export", "websis_export"}
    normalized = (import_source or "manual").strip().lower()
    return normalized if normalized in allowed else "manual"


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
    candidates = _extract_course_code_candidates(import_text)
    matched = sorted(code for code in candidates if code in known_codes)
    unknown = sorted(code for code in candidates if code not in known_codes)

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
        matched_course_codes=matched,
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

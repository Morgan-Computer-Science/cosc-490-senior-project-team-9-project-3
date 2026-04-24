import re
from collections import Counter
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.db import get_db
from app.rag import (
    canonicalize_course_code,
    find_program_row,
    load_degree_requirement_rows,
    load_department_rows,
    load_faculty_rows,
    load_program_rows,
    load_support_resource_rows,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])
COURSE_PREFIX_PATTERN = re.compile(r"^[A-Z]+")
GENERAL_CATALOG_PREFIXES = {"ENGL", "COMM", "HIST", "HLTH", "EDUC"}
MAJOR_PREFIX_FAMILIES: dict[str, set[str]] = {
    "Computer Science": {"COSC"},
    "Information Science": {"INSS"},
    "Cloud Computing": {"CLDC"},
    "Nursing": {"NURS"},
    "Biology": {"BIOL"},
    "Psychology": {"PSYC"},
    "Criminal Justice": {"CRJU"},
    "Elementary Education": {"EDUC"},
    "Accounting": {"ACCT"},
    "Finance": {"FINA"},
    "Business Administration": {"BUSN", "MGMT"},
    "Marketing": {"MKTG"},
}


def _normalize(value: Optional[str]) -> str:
    return (value or "").strip()


def _required_course_codes_for_major(major: Optional[str]) -> list[str]:
    normalized_major = _normalize(major)
    if not normalized_major:
        return []

    program_row = find_program_row(normalized_major)
    canonical_major = _normalize(program_row.get("canonical_major")) if program_row else normalized_major
    matching_row = next(
        (
            row
            for row in load_degree_requirement_rows()
            if _normalize(row.get("major")).lower() == canonical_major.lower()
        ),
        None,
    )
    if not matching_row:
        return []

    seen: set[str] = set()
    required_codes: list[str] = []
    for raw_code in _normalize(matching_row.get("required_courses")).split(";"):
        normalized_code = canonicalize_course_code(raw_code)
        if not normalized_code or normalized_code in seen:
            continue
        seen.add(normalized_code)
        required_codes.append(normalized_code)
    return required_codes


def _course_prefix(code: str) -> str:
    match = COURSE_PREFIX_PATTERN.match(_normalize(code).upper())
    return match.group(0) if match else ""


def _catalog_prefixes_for_major(major: Optional[str]) -> list[str]:
    normalized_major = _normalize(major)
    if not normalized_major:
        return []

    program_row = find_program_row(normalized_major)
    canonical_major = _normalize(program_row.get("canonical_major")) if program_row else normalized_major

    explicit_prefixes = MAJOR_PREFIX_FAMILIES.get(canonical_major)
    if explicit_prefixes:
        return sorted(explicit_prefixes)

    required_codes = _required_course_codes_for_major(canonical_major)
    if not required_codes:
        return []

    prefix_counts = Counter(_course_prefix(code) for code in required_codes if _course_prefix(code))
    if not prefix_counts:
        return []

    non_general_counts = Counter(
        {
            prefix: count
            for prefix, count in prefix_counts.items()
            if prefix not in GENERAL_CATALOG_PREFIXES
        }
    )
    effective_counts = non_general_counts or prefix_counts
    dominant_count = max(effective_counts.values())
    return sorted(prefix for prefix, count in effective_counts.items() if count == dominant_count)


@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(
    search: Optional[str] = None,
    level: Optional[str] = None,
    department: Optional[str] = None,
    major: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Course)

    if search:
        query = query.filter(
            models.Course.title.contains(search) | models.Course.code.contains(search)
        )
    if level:
        normalized_level = level.strip()
        if len(normalized_level) == 1 and normalized_level.isdigit():
            normalized_level = f"{normalized_level}00"
        query = query.filter(models.Course.level == normalized_level)
    if major:
        catalog_prefixes = _catalog_prefixes_for_major(major)
        if not catalog_prefixes:
            return []
        prefix_filters = [models.Course.code.like(f"{prefix}%") for prefix in catalog_prefixes]
        query = query.filter(or_(*prefix_filters))
    if department:
        query = query.filter(models.Course.department == department.strip())

    return query.order_by(models.Course.code.asc()).all()


@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/courses", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_course = models.Course(**course.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/departments", response_model=List[schemas.DepartmentInfo])
def list_departments(
    current_user: models.User = Depends(get_current_user),
):
    return [schemas.DepartmentInfo(**row) for row in load_department_rows()]


@router.get("/programs", response_model=List[schemas.ProgramInfo])
def list_programs(
    current_user: models.User = Depends(get_current_user),
):
    return [schemas.ProgramInfo(**row) for row in load_program_rows()]


@router.get("/faculty", response_model=List[schemas.FacultyInfo])
def list_faculty(
    current_user: models.User = Depends(get_current_user),
):
    return [schemas.FacultyInfo(**row) for row in load_faculty_rows()]


@router.get("/support-resources", response_model=List[schemas.SupportResourceInfo])
def list_support_resources(
    current_user: models.User = Depends(get_current_user),
):
    return [schemas.SupportResourceInfo(**row) for row in load_support_resource_rows()]

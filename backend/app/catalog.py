from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db
from .auth import get_current_user  # same dependency used by /auth/me

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
)

# ---------- Courses ----------


@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(
    search: Optional[str] = None,
    level: Optional[str] = None,
    semester: Optional[str] = None,
    min_credits: Optional[int] = None,
    max_credits: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List courses with simple filters:
    - search: matches code/title/description
    - level: exact match (e.g. 'Undergraduate')
    - semester: substring match on semester_offered (e.g. 'Fall')
    - min_credits/max_credits: numeric filters
    """
    query = db.query(models.Course)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Course.code.ilike(like)) |
            (models.Course.title.ilike(like)) |
            (models.Course.description.ilike(like))
        )

    if level:
        query = query.filter(models.Course.level == level)

    if semester:
        like = f"%{semester}%"
        query = query.filter(models.Course.semester_offered.ilike(like))

    if min_credits is not None:
        query = query.filter(models.Course.credits >= min_credits)

    if max_credits is not None:
        query = query.filter(models.Course.credits <= max_credits)

    return query.order_by(models.Course.code).all()


@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


# ---------- Faculty ----------


@router.get("/faculty", response_model=List[schemas.FacultyOut])
def list_faculty(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List faculty with optional search on name/title/email.
    """
    query = db.query(models.Faculty)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Faculty.name.ilike(like)) |
            (models.Faculty.title.ilike(like)) |
            (models.Faculty.email.ilike(like))
        )

    return query.order_by(models.Faculty.name).all()


@router.get("/faculty/{faculty_id}", response_model=schemas.FacultyOut)
def get_faculty(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    faculty = (
        db.query(models.Faculty)
        .filter(models.Faculty.id == faculty_id)
        .first()
    )
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty member not found",
        )
    return faculty
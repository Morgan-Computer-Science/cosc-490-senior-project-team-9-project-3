from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.db import get_db

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(
    search: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Course)

    if search:
        query = query.filter(
            models.Course.title.contains(search) | models.Course.code.contains(search)
        )
    if level:
        query = query.filter(models.Course.code.startswith(level))

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

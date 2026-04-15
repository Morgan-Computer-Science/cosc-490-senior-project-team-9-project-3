from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.db import get_db
from app.rag import load_department_rows, load_faculty_rows, load_support_resource_rows

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


@router.get("/departments", response_model=List[schemas.DepartmentInfo])
def list_departments(
    current_user: models.User = Depends(get_current_user),
):
    return [schemas.DepartmentInfo(**row) for row in load_department_rows()]


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

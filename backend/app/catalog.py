from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas, security
from app.db import get_db

router = APIRouter(prefix="/catalog", tags=["catalog"])

# --- COURSE ROUTES ---

@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(
    search: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    query = db.query(models.Course)
    if search:
        query = query.filter(models.Course.title.contains(search) | models.Course.code.contains(search))
    if level:
        query = query.filter(models.Course.code.startswith(level))
    return query.all()

@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def get_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.post("/courses", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    course: schemas.CourseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    new_course = models.Course(**course.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

# --- FACULTY ROUTES ---

@router.get("/faculty", response_model=List[schemas.FacultyOut])
def list_faculty(
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    query = db.query(models.Faculty)
    if department:
        query = query.filter(models.Faculty.department == department)
    return query.all()

@router.post("/faculty", response_model=schemas.FacultyOut, status_code=status.HTTP_201_CREATED)
def create_faculty(
    faculty: schemas.FacultyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    new_faculty = models.Faculty(**faculty.model_dump())
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)
    return new_faculty
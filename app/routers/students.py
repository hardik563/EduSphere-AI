from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentPatch,
    StudentResponse,
    StudentListResponse,
    DashboardStatsResponse,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Registers a new student with validation. Student ID must be unique."
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db)
):
    existing = crud.get_student_by_student_id(db, student_in.student_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with ID '{student_in.student_id}' already exists."
        )

    try:
        new_student = crud.create_student(db, student_in)
        return new_student
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create student: {str(e)}"
        )


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List and filter students",
    description="Returns a paginated list of students with optional search query, course filter, and sorting."
)
def list_students(
    search: Optional[str] = Query(None, description="Search by name, ID, email, or phone"),
    course: Optional[str] = Query(None, description="Filter by course title"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g. full_name, student_id, enrollment_date)"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    items, total = crud.get_students(
        db,
        search=search,
        course=course,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    page = (skip // limit) + 1

    return StudentListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        items=items
    )


@router.get(
    "/stats/summary",
    response_model=DashboardStatsResponse,
    summary="Get student dashboard metrics",
    description="Aggregates student counts, course breakdown, and recent registrations."
)
def get_dashboard_summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@router.get(
    "/meta/courses",
    response_model=List[str],
    summary="List all distinct courses",
    description="Returns an alphabetically sorted list of courses currently registered."
)
def get_courses(db: Session = Depends(get_db)):
    return crud.get_all_courses(db)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Retrieve a specific student",
    description="Fetches full details for a student using their unique student_id."
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Replace or update a student",
    description="Performs a complete update of a student's profile."
)
def update_student(
    student_id: str,
    update_in: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )

    try:
        updated = crud.update_student(db, student, update_in)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update student: {str(e)}"
        )


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partially update a student",
    description="Updates only the supplied fields of a student's profile."
)
def patch_student(
    student_id: str,
    patch_in: StudentPatch,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )

    try:
        updated = crud.patch_student(db, student, patch_in)
        return updated
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to patch student: {str(e)}"
        )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a student",
    description="Removes a student permanently from the database."
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )

    deleted_id = student.student_id
    deleted_name = student.full_name
    crud.delete_student(db, student)
    return {
        "status": "success",
        "message": f"Student '{deleted_name}' (ID: {deleted_id}) has been permanently deleted.",
        "student_id": deleted_id
    }

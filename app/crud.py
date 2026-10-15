from datetime import date
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import or_, func, desc, asc
from sqlalchemy.orm import Session
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentPatch


def get_student_by_student_id(db: Session, student_id: str) -> Optional[Student]:
    """Retrieve student by unique student_id (case-insensitive)."""
    return db.query(Student).filter(func.upper(Student.student_id) == student_id.strip().upper()).first()


def get_student_by_id(db: Session, id: int) -> Optional[Student]:
    """Retrieve student by internal primary key."""
    return db.query(Student).filter(Student.id == id).first()


def get_students(
    db: Session,
    search: Optional[str] = None,
    course: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc"
) -> Tuple[List[Student], int]:
    """
    List students with optional search, course filter, pagination, and sorting.
    Returns (items, total_count).
    """
    query = db.query(Student)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.student_id.ilike(search_term),
                Student.full_name.ilike(search_term),
                Student.email.ilike(search_term),
                Student.phone.ilike(search_term),
            )
        )

    if course and course.strip():
        query = query.filter(Student.course.ilike(course.strip()))

    total = query.count()

    # Determine sort attribute
    sort_column = getattr(Student, sort_by, Student.created_at)
    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    items = query.offset(skip).limit(limit).all()
    return items, total


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create a new student record."""
    db_student = Student(
        student_id=student_in.student_id,
        full_name=student_in.full_name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date or date.today(),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, db_student: Student, update_in: StudentUpdate) -> Student:
    """Full update of student details."""
    db_student.full_name = update_in.full_name
    db_student.date_of_birth = update_in.date_of_birth
    db_student.email = update_in.email
    db_student.phone = update_in.phone
    db_student.course = update_in.course
    db_student.address = update_in.address
    if update_in.enrollment_date is not None:
        db_student.enrollment_date = update_in.enrollment_date

    db.commit()
    db.refresh(db_student)
    return db_student


def patch_student(db: Session, db_student: Student, patch_in: StudentPatch) -> Student:
    """Partial update of student details."""
    update_data = patch_in.model_dump(exclude_unset=True)

    # Validate contact rule if both are set to None
    new_email = update_data.get("email", db_student.email)
    new_phone = update_data.get("phone", db_student.phone)
    if not new_email and not new_phone:
        raise ValueError("Cannot remove both email and phone; at least one contact method must remain.")

    for field, val in update_data.items():
        setattr(db_student, field, val)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """Delete a student record."""
    db.delete(db_student)
    db.commit()


def get_all_courses(db: Session) -> List[str]:
    """Retrieve distinct course names that are non-empty."""
    results = db.query(Student.course).filter(Student.course.isnot(None), Student.course != "").distinct().all()
    courses = [r[0] for r in results if r[0]]
    courses.sort()
    return courses


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Calculate dashboard metrics."""
    total = db.query(Student).count()

    course_groups = (
        db.query(Student.course, func.count(Student.id))
        .group_by(Student.course)
        .order_by(desc(func.count(Student.id)))
        .all()
    )

    distribution = []
    distinct_courses_count = 0
    for course_name, count in course_groups:
        display_name = course_name if course_name else "Unassigned / General"
        if course_name:
            distinct_courses_count += 1
        pct = round((count / total * 100), 1) if total > 0 else 0
        distribution.append({
            "course": display_name,
            "count": count,
            "percentage": pct
        })

    recent_students = db.query(Student).order_by(desc(Student.created_at)).limit(5).all()

    # Calculate unique email domains as extra stat
    all_emails = db.query(Student.email).filter(Student.email.isnot(None)).all()
    domains = set()
    for (em,) in all_emails:
        if em and "@" in em:
            domains.add(em.split("@")[-1].lower())

    return {
        "total_students": total,
        "courses_count": distinct_courses_count,
        "course_distribution": distribution,
        "recent_students": recent_students,
        "unique_domains": len(domains)
    }


# ==========================================================
# Controlled queries for AI assistant (No unrestricted SQL)
# ==========================================================

def ai_query_total_students(db: Session) -> Dict[str, Any]:
    count = db.query(Student).count()
    return {"total_students": count}


def ai_query_by_course(db: Session, course_search: str) -> List[Dict[str, Any]]:
    students = db.query(Student).filter(Student.course.ilike(f"%{course_search.strip()}%")).all()
    return [s.to_dict() for s in students]


def ai_query_by_birth_year(db: Session, year: int, comparison: str = "after") -> List[Dict[str, Any]]:
    """Safe structured query for birth year."""
    if comparison == "after":
        cutoff = date(year, 12, 31)
        students = db.query(Student).filter(Student.date_of_birth > cutoff).order_by(Student.date_of_birth.asc()).all()
    elif comparison == "before":
        cutoff = date(year, 1, 1)
        students = db.query(Student).filter(Student.date_of_birth < cutoff).order_by(Student.date_of_birth.desc()).all()
    else:  # equal / in that year
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        students = db.query(Student).filter(Student.date_of_birth.between(start, end)).all()

    return [s.to_dict() for s in students]


def ai_query_by_contact(db: Session, term: str) -> List[Dict[str, Any]]:
    clean = term.strip()
    students = db.query(Student).filter(
        or_(
            Student.email.ilike(f"%{clean}%"),
            Student.phone.ilike(f"%{clean}%")
        )
    ).all()
    return [s.to_dict() for s in students]


def ai_query_course_distribution(db: Session) -> List[Dict[str, Any]]:
    stats = get_dashboard_stats(db)
    return stats["course_distribution"]


def ai_get_comprehensive_context(db: Session) -> Dict[str, Any]:
    """Fetches a sanitized snapshot of database statistics and sample records for LLM context grounding."""
    stats = get_dashboard_stats(db)
    all_students = db.query(Student).limit(50).all()
    return {
        "total_count": stats["total_students"],
        "courses": [d["course"] for d in stats["course_distribution"]],
        "course_distribution": stats["course_distribution"],
        "sample_students": [
            {
                "student_id": s.student_id,
                "full_name": s.full_name,
                "course": s.course,
                "dob": s.date_of_birth.isoformat() if s.date_of_birth else None,
                "email": s.email,
                "phone": s.phone,
                "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None
            }
            for s in all_students
        ]
    }

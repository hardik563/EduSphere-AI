from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Student

SAMPLE_STUDENTS = [
    {
        "student_id": "STU-2025-001",
        "full_name": "Aarav Sharma",
        "date_of_birth": date(2004, 5, 15),
        "email": "aarav.sharma@example.com",
        "phone": "+91 9876543210",
        "course": "Computer Science",
        "address": "42 Tech Boulevard, Koramangala, Bangalore",
        "enrollment_date": date(2025, 8, 1),
    },
    {
        "student_id": "STU-2025-002",
        "full_name": "Diya Patel",
        "date_of_birth": date(2006, 3, 22),
        "email": "diya.patel@example.com",
        "phone": "+91 9822334455",
        "course": "Artificial Intelligence",
        "address": "15 Green Meadows, Vastrapur, Ahmedabad",
        "enrollment_date": date(2025, 8, 1),
    },
    {
        "student_id": "STU-2025-003",
        "full_name": "Rohan Verma",
        "date_of_birth": date(2003, 11, 9),
        "email": "rohan.verma@example.com",
        "phone": "+91 9811223344",
        "course": "Data Science",
        "address": "78 Civil Lines, Jaipur, Rajasthan",
        "enrollment_date": date(2024, 8, 10),
    },
    {
        "student_id": "STU-2025-004",
        "full_name": "Ananya Iyer",
        "date_of_birth": date(2006, 8, 14),
        "email": "ananya.iyer@example.com",
        "phone": "+91 9940112233",
        "course": "Computer Science",
        "address": "29 Temple Street, Mylapore, Chennai",
        "enrollment_date": date(2025, 8, 5),
    },
    {
        "student_id": "STU-2025-005",
        "full_name": "Vikram Singh",
        "date_of_birth": date(2004, 1, 30),
        "email": "vikram.singh@example.com",
        "phone": "+91 9765432109",
        "course": "Electronics & Communication",
        "address": "104 Gomti Nagar, Lucknow, Uttar Pradesh",
        "enrollment_date": date(2024, 8, 12),
    },
    {
        "student_id": "STU-2025-006",
        "full_name": "Priya Nair",
        "date_of_birth": date(2005, 9, 19),
        "email": "priya.nair@example.com",
        "phone": "+91 9447123456",
        "course": "Artificial Intelligence",
        "address": "56 Hill View Colony, Kochi, Kerala",
        "enrollment_date": date(2025, 8, 2),
    },
    {
        "student_id": "STU-2025-007",
        "full_name": "Siddharth Roy",
        "date_of_birth": date(2003, 7, 25),
        "email": "siddharth.roy@example.com",
        "phone": "+91 9830987654",
        "course": "Mechanical Engineering",
        "address": "88 Park Circus, Kolkata, West Bengal",
        "enrollment_date": date(2023, 8, 15),
    },
    {
        "student_id": "STU-2025-008",
        "full_name": "Sneha Kulkarni",
        "date_of_birth": date(2007, 2, 10),
        "email": "sneha.kulkarni@example.com",
        "phone": "+91 9123456789",
        "course": "Data Science",
        "address": "12 Shivajinagar, Pune, Maharashtra",
        "enrollment_date": date(2025, 8, 3),
    },
    {
        "student_id": "STU-2025-009",
        "full_name": "Kabir Das",
        "date_of_birth": date(2004, 12, 5),
        "email": "kabir.das@example.com",
        "phone": "+91 9871122334",
        "course": "Computer Science",
        "address": "63 Hauz Khas, New Delhi",
        "enrollment_date": date(2024, 8, 14),
    },
    {
        "student_id": "STU-2025-010",
        "full_name": "Meera Sen",
        "date_of_birth": date(2005, 4, 18),
        "email": "meera.sen@example.com",
        "phone": "+91 9988776655",
        "course": "Business Analytics",
        "address": "33 Banjara Hills, Hyderabad, Telangana",
        "enrollment_date": date(2025, 8, 4),
    }
]


def seed_database(db: Session = None, force_reset: bool = False) -> int:
    """Populates database with realistic sample student records if empty or if force_reset is True."""
    Base.metadata.create_all(bind=engine)
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        existing_count = db.query(Student).count()
        if existing_count > 0 and not force_reset:
            return existing_count

        if force_reset:
            db.query(Student).delete()
            db.commit()

        count = 0
        for student_data in SAMPLE_STUDENTS:
            existing = db.query(Student).filter(Student.student_id == student_data["student_id"]).first()
            if not existing:
                s = Student(**student_data)
                db.add(s)
                count += 1

        db.commit()
        return db.query(Student).count()
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    count = seed_database()
    print(f"Database seeded successfully. Total students: {count}")

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(120), unique=False, index=True, nullable=True)
    phone = Column(String(30), unique=False, index=True, nullable=True)
    course = Column(String(100), index=True, nullable=True)
    address = Column(Text, nullable=True)
    enrollment_date = Column(Date, nullable=True, default=date.today)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "email": self.email,
            "phone": self.phone,
            "course": self.course,
            "address": self.address,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

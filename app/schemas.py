from datetime import date, datetime
from typing import Optional, List, Dict
import re
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PHONE_REGEX = r"^(\+?[0-9]{1,4}[\s-]?)?(\(?[0-9]{2,5}\)?[\s-]?)?[0-9]{3,5}[\s-]?[0-9]{3,5}$"


class StudentBase(BaseModel):
    student_id: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique Student ID (e.g., STU-2025-001)",
        examples=["STU-2025-001"]
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full Name of the student",
        examples=["Aarav Sharma"]
    )
    date_of_birth: date = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        examples=["2004-05-15"]
    )
    email: Optional[str] = Field(
        default=None,
        description="Valid email address",
        examples=["aarav.sharma@example.com"]
    )
    phone: Optional[str] = Field(
        default=None,
        description="Contact phone number",
        examples=["+91 9876543210"]
    )
    course: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Course or major enrolled in",
        examples=["Computer Science"]
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Residential address",
        examples=["124 Tech Park Road, Bangalore, Karnataka"]
    )
    enrollment_date: Optional[date] = Field(
        default=None,
        description="Date of enrollment (defaults to current date)",
        examples=["2025-08-01"]
    )

    @field_validator("student_id")
    @classmethod
    def clean_student_id(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if not re.match(r"^[A-Z0-9\-_]{2,50}$", cleaned):
            raise ValueError("Student ID may only contain uppercase letters, numbers, hyphens, and underscores.")
        return cleaned

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if not re.match(EMAIL_REGEX, cleaned):
            raise ValueError("Invalid email format.")
        return cleaned.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if not re.match(PHONE_REGEX, cleaned):
            raise ValueError("Invalid phone format (e.g. +91 9876543210 or 9876543210).")
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Date of birth must be in the past.")
        age_years = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age_years < 3:
            raise ValueError("Student must be at least 3 years of age.")
        if age_years > 100:
            raise ValueError("Student age exceeds valid range.")
        return v


class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def check_contact_provided(self):
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone number) must be provided.")
        if self.enrollment_date is None:
            self.enrollment_date = date.today()
        return self


class StudentUpdate(BaseModel):
    """Full update schema for PUT /students/{student_id}."""
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if not re.match(EMAIL_REGEX, cleaned):
            raise ValueError("Invalid email format.")
        return cleaned.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if not re.match(PHONE_REGEX, cleaned):
            raise ValueError("Invalid phone format.")
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Date of birth must be in the past.")
        return v

    @model_validator(mode="after")
    def check_contact(self):
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone number) must be provided.")
        return self


class StudentPatch(BaseModel):
    """Partial update schema for PATCH /students/{student_id}."""
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if len(cleaned) < 2:
                raise ValueError("Full name must be at least 2 characters.")
            return cleaned
        return None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if cleaned and not re.match(EMAIL_REGEX, cleaned):
                raise ValueError("Invalid email format.")
            return cleaned.lower() if cleaned else None
        return None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if cleaned and not re.match(PHONE_REGEX, cleaned):
                raise ValueError("Invalid phone format.")
            return cleaned if cleaned else None
        return None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v >= date.today():
            raise ValueError("Date of birth must be in the past.")
        return v


class StudentResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[StudentResponse]


class DashboardStatsResponse(BaseModel):
    total_students: int
    courses_count: int
    course_distribution: List[Dict[str, object]]
    recent_students: List[StudentResponse]
    unique_domains: int


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Natural language question")


class AIChatResponse(BaseModel):
    query: str
    answer: str
    grounded_data: Optional[Dict[str, object]] = None
    source: str = Field(..., description="Source of generation: 'ollama' or 'grounded_rules'")
    model: Optional[str] = None
    ollama_available: bool
    suggestions: List[str] = []

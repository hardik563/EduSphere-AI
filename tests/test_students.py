import tempfile
import os
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Student, Base
from app import crud


def test_create_student_success(client):
    payload = {
        "student_id": "STU-TEST-001",
        "full_name": "Test Student One",
        "date_of_birth": "2004-06-15",
        "email": "test.one@example.com",
        "phone": "+91 9876500001",
        "course": "Computer Science",
        "address": "123 Innovation Way, Tech Park",
        "enrollment_date": "2025-08-01"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-TEST-001"
    assert data["full_name"] == "Test Student One"
    assert data["email"] == "test.one@example.com"
    assert "id" in data


def test_create_student_duplicate_id_fails(client):
    payload = {
        "student_id": "STU-DUP-001",
        "full_name": "Original Student",
        "date_of_birth": "2004-01-10",
        "email": "orig@example.com",
        "course": "Data Science"
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    # Attempt to create duplicate
    dup_payload = {
        "student_id": "STU-DUP-001",
        "full_name": "Duplicate Student",
        "date_of_birth": "2005-02-14",
        "email": "dup@example.com",
        "course": "Data Science"
    }
    res2 = client.post("/students", json=dup_payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_create_student_missing_contact_fails(client):
    payload = {
        "student_id": "STU-NOCONTACT-01",
        "full_name": "No Contact Student",
        "date_of_birth": "2004-05-15",
        # Neither email nor phone provided
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "contact" in str(response.json()).lower()


def test_create_student_invalid_email_fails(client):
    payload = {
        "student_id": "STU-BADEMAIL-01",
        "full_name": "Bad Email Student",
        "date_of_birth": "2004-05-15",
        "email": "not-a-valid-email-string"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "Invalid email format" in str(response.json())


def test_create_student_future_dob_fails(client):
    payload = {
        "student_id": "STU-FUTURE-01",
        "full_name": "Time Traveler",
        "date_of_birth": "2099-01-01",
        "email": "timetraveler@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "past" in str(response.json()).lower()


def test_list_students_and_pagination(client):
    # Create 3 students
    for i in range(1, 4):
        client.post("/students", json={
            "student_id": f"STU-LIST-{i:03d}",
            "full_name": f"Student List {i}",
            "date_of_birth": "2004-01-01",
            "email": f"list{i}@example.com",
            "course": "Computer Science" if i % 2 == 0 else "Information Technology"
        })

    response = client.get("/students?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 2


def test_list_students_search_by_name_and_id(client):
    client.post("/students", json={
        "student_id": "STU-FIND-999",
        "full_name": "Unique Searchable Name",
        "date_of_birth": "2003-08-20",
        "email": "unique.find@example.com"
    })

    # Search by full name
    res_name = client.get("/students?search=Unique")
    assert res_name.status_code == 200
    assert any(s["student_id"] == "STU-FIND-999" for s in res_name.json()["items"])

    # Search by ID
    res_id = client.get("/students?search=FIND-999")
    assert res_id.status_code == 200
    assert len(res_id.json()["items"]) == 1
    assert res_id.json()["items"][0]["full_name"] == "Unique Searchable Name"


def test_list_students_filter_by_course(client):
    client.post("/students", json={
        "student_id": "STU-CRSE-1",
        "full_name": "AI Specialist",
        "date_of_birth": "2004-03-10",
        "email": "ai.student@example.com",
        "course": "Artificial Intelligence"
    })
    client.post("/students", json={
        "student_id": "STU-CRSE-2",
        "full_name": "Mech Specialist",
        "date_of_birth": "2004-03-10",
        "email": "mech.student@example.com",
        "course": "Mechanical Engineering"
    })

    res = client.get("/students?course=Artificial Intelligence")
    assert res.status_code == 200
    items = res.json()["items"]
    assert all(s["course"] == "Artificial Intelligence" for s in items)
    assert any(s["student_id"] == "STU-CRSE-1" for s in items)


def test_get_student_by_id_success(client):
    client.post("/students", json={
        "student_id": "STU-GET-001",
        "full_name": "Specific Student",
        "date_of_birth": "2005-07-12",
        "email": "specific@example.com"
    })

    res = client.get("/students/STU-GET-001")
    assert res.status_code == 200
    assert res.json()["full_name"] == "Specific Student"


def test_get_student_by_id_not_found(client):
    res = client.get("/students/NONEXISTENT-ID")
    assert res.status_code == 404
    assert "was not found" in res.json()["detail"]


def test_put_update_student_full(client):
    client.post("/students", json={
        "student_id": "STU-PUT-001",
        "full_name": "Initial Name",
        "date_of_birth": "2004-01-01",
        "email": "initial@example.com",
        "course": "Computer Science"
    })

    put_payload = {
        "full_name": "Updated Name Full",
        "date_of_birth": "2004-02-02",
        "email": "updated@example.com",
        "phone": "+91 9999988888",
        "course": "Data Science",
        "address": "New Address Street",
        "enrollment_date": "2025-09-01"
    }

    res = client.put("/students/STU-PUT-001", json=put_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Updated Name Full"
    assert data["course"] == "Data Science"
    assert data["email"] == "updated@example.com"
    assert data["address"] == "New Address Street"


def test_patch_update_student_partial(client):
    client.post("/students", json={
        "student_id": "STU-PATCH-001",
        "full_name": "Patch Target",
        "date_of_birth": "2004-05-15",
        "email": "original.patch@example.com",
        "course": "Physics"
    })

    # Only patch course and phone
    patch_payload = {
        "course": "Quantum Computing",
        "phone": "+91 8888877777"
    }
    res = client.patch("/students/STU-PATCH-001", json=patch_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["course"] == "Quantum Computing"
    assert data["phone"] == "+91 8888877777"
    assert data["full_name"] == "Patch Target"  # preserved unchanged
    assert data["email"] == "original.patch@example.com"  # preserved unchanged


def test_delete_student_success(client):
    client.post("/students", json={
        "student_id": "STU-DEL-001",
        "full_name": "To Be Deleted",
        "date_of_birth": "2004-10-10",
        "email": "delete.me@example.com"
    })

    # Verify exists
    assert client.get("/students/STU-DEL-001").status_code == 200

    # Delete
    del_res = client.delete("/students/STU-DEL-001")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Verify deleted
    assert client.get("/students/STU-DEL-001").status_code == 404


def test_delete_student_not_found(client):
    res = client.delete("/students/DOES-NOT-EXIST")
    assert res.status_code == 404


def test_sqlite_persistence_across_sessions():
    """Verify that student records persist to the SQLite database file across engine & session restarts."""
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)

    try:
        url = f"sqlite:///{temp_db_path}"
        engine1 = create_engine(url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(bind=engine1)
        session1 = Session1()

        # Add record
        student = Student(
            student_id="STU-PERSIST-1",
            full_name="Persisted Student",
            date_of_birth=date(2004, 3, 1),
            email="persist@example.com",
            course="Robotics"
        )
        session1.add(student)
        session1.commit()
        session1.close()
        engine1.dispose()

        # Reopen completely new engine on the same SQLite file
        engine2 = create_engine(url, connect_args={"check_same_thread": False})
        Session2 = sessionmaker(bind=engine2)
        session2 = Session2()

        retrieved = session2.query(Student).filter(Student.student_id == "STU-PERSIST-1").first()
        assert retrieved is not None
        assert retrieved.full_name == "Persisted Student"
        assert retrieved.course == "Robotics"
        session2.close()
        engine2.dispose()
    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


def test_ai_assistant_grounded_response(client):
    client.post("/students", json={
        "student_id": "STU-AI-001",
        "full_name": "Artificial Intelligence Learner",
        "date_of_birth": "2006-04-12",
        "email": "ai.learner@example.com",
        "course": "Computer Science"
    })

    # Query total students
    res = client.post("/api/ai/chat", json={"message": "How many students are registered?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "registered" in data["answer"].lower() or "student" in data["answer"].lower()

    # Query born after 2005
    res_dob = client.post("/api/ai/chat", json={"message": "Which students were born after 2005?"})
    assert res_dob.status_code == 200
    assert "Artificial Intelligence Learner" in res_dob.json()["answer"]


def test_ai_status_endpoint(client):
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "ollama_available" in data
    assert "configured_model" in data


def test_dashboard_stats_summary(client):
    res = client.get("/students/stats/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_students" in data
    assert "courses_count" in data
    assert "course_distribution" in data

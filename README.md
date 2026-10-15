# EduSphere AI — Smart Student Management System

[![Python](https://img.shields.io/badge/Python-3.13+-teal.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy_2.0-0284c7.svg)](https://www.sqlite.org/)
[![AI-Grounded](https://img.shields.io/badge/AI-Ollama_Ready-10b981.svg)](https://ollama.ai/)
[![Tests](https://img.shields.io/badge/Pytest-18%20Passed-success.svg)](https://pytest.org/)

**EduSphere AI** is a production-grade, full-stack student records platform developed as part of the **Python/AI-ML internship at EWB Edu Tech Pvt. Ltd.** It pairs a high-performance **FastAPI** backend and **SQLite** database with an elegant, modern web interface and a local conversational **AI Assistant** grounded strictly in verifiable student data.


<img width="1905" height="1040" alt="image" src="https://github.com/user-attachments/assets/b0b95891-1479-4c91-aaa3-55f9a57b7026" />

---

<img width="1877" height="961" alt="image" src="https://github.com/user-attachments/assets/87803b17-836b-4f0a-ac17-aef7a0691bfc" />


## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Project Architecture & Directory Structure](#-project-architecture--directory-structure)
5. [Prerequisites](#-prerequisites)
6. [Installation & Setup](#-installation--setup)
7. [Running the Application](#-running-the-application)
8. [API Documentation & Mandatory Endpoints](#-api-documentation--mandatory-endpoints)
9. [Example API Requests & Responses](#-example-api-requests--responses)
10. [Optional AI Assistant (Ollama Integration)](#-optional-ai-assistant-ollama-integration)
11. [Running the Automated Test Suite](#-running-the-automated-test-suite)
12. [Troubleshooting & Common Questions](#-troubleshooting--common-questions)
13. [Internship Submission Notes](#-internship-submission-notes)

---

<img width="1860" height="910" alt="image" src="https://github.com/user-attachments/assets/1a1ed242-11e2-43eb-8443-0207920c8085" />


## 🌟 Project Overview

Managing student academic records should be fast, reliable, and intelligent. EduSphere AI replaces clunky spreadsheets and outdated dashboards with:
- **Rock-solid Data Validation**: Every student attribute (ID format, age threshold, email/phone format) is enforced by **Pydantic v2**.
- **RESTful Architecture**: Complete implementation of mandatory CRUD operations with precise HTTP semantics (`200`, `201`, `400`, `404`, `409`, `422`).
- **Data Persistence**: SQLite database via **SQLAlchemy 2.0 ORM** ensuring zero record loss on restarts.
- **Modern UI/UX**: Warm-white background, soft teal and mint accents, real-time debounced search, course filters, and animated modals.
- **Safe AI Assistant**: Answers natural-language questions through controlled backend retrieval without raw SQL execution risks. Works out-of-the-box in deterministic grounded mode, and connects seamlessly to local **Ollama** when available.

---

## ✨ Key Features

### 1. Student Record Management (CRUD)
- **Add Student**: Form with real-time validation, duplicate ID protection, and an "Auto Generate ID" tool.
- **Search & Filter**: Instant search across Student Name, ID, Email, and Phone number; filter by Academic Course.
- **View Profile**: Detailed modal with computed student age, contact links, academic enrollment details, and audit timestamps.
- **Full & Partial Updates**: Supports both full replacement (`PUT`) and field-level modification (`PATCH`).
- **Safe Deletion**: Two-step confirmation modal preventing accidental deletions.
- **Automatic Seed Data**: Includes 10 realistic sample student records spanning multiple courses and birth years.

### 2. Executive Dashboard
- **Live KPI Metrics**: Real-time counter of total registered students, distinct courses, and recent enrollments.
- **Course Distribution**: Visual progress breakdown showing student percentages across faculties.
- **Recently Enrolled Table**: Quick-action view for the most recent 5 registrations.

### 3. EduSphere AI Assistant
- **Grounded Natural Language Answers**: Answers queries like:
  - *"How many students are registered?"*
  - *"Show students enrolled in Computer Science."*
  - *"Which students were born after 2005?"*
  - *"Find students using aarav.sharma@example.com"*
  - *"Summarize the student distribution by course."*
- **Safety First**: Never runs unrestricted SQL. All answers are synthesized from controlled SQLAlchemy queries.
- **Graceful Fallback**: If Ollama is offline, the built-in deterministic query engine provides accurate answers with clear setup instructions to connect local LLMs.

---


<img width="1903" height="976" alt="image" src="https://github.com/user-attachments/assets/3cc93f67-a925-43b3-8269-79959b5b4177" />

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Python 3.13+ / FastAPI 0.115+ | High-throughput asynchronous REST API |
| **Database** | SQLite 3 | Embedded, zero-configuration persistent SQL storage |
| **ORM** | SQLAlchemy 2.0+ | Declarative database modeling, queries, and migrations |
| **Data Validation** | Pydantic v2 & Pydantic-Settings | Strict request/response schemas and environment configuration |
| **Frontend UI** | HTML5, Vanilla CSS3, Modern ES6+ JavaScript | Fast, responsive interface without bloated heavy frameworks |
| **Typography & Styling**| Plus Jakarta Sans, Custom Design Tokens | Soft teal (`#0d9488`), mint (`#10b981`), warm white palette |
| **Testing** | Pytest 8.4+, HTTPX, Starlette TestClient | Unit, integration, and persistence test suite |
| **AI Integration** | Ollama REST API (`llama3.2`, `mistral`, `phi3`) | Optional local LLM conversational reasoning |

---

![Uploading image.png…]()


## 📂 Project Architecture & Directory Structure

```
EduSphere AI/
├── app/
│   ├── __init__.py               # Application package definition
│   ├── main.py                   # FastAPI initialization, lifespan & exception handlers
│   ├── config.py                 # Pydantic Settings and environment management
│   ├── database.py               # SQLAlchemy engine, session maker, and DB dependency
│   ├── models.py                 # SQLAlchemy Student ORM model
│   ├── schemas.py                # Pydantic request/response schemas & validators
│   ├── crud.py                   # Database access operations & controlled AI queries
│   ├── seed.py                   # Initial fictional sample student data generator
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py           # Mandatory REST CRUD endpoints (/students)
│   │   └── ai.py                 # AI assistant and status endpoints (/api/ai)
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py         # Grounded retrieval engine & Ollama client
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Warm-white, teal & mint design system
│   │   ├── js/
│   │   │   └── app.js            # DOM state management, REST fetch, and chat UI
│   │   └── img/
│   │       └── logo.svg          # EduSphere AI brand vector graphic
│   └── templates/
│       └── index.html            # Main single-page application dashboard
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Isolated in-memory SQLite fixtures & TestClient
│   └── test_students.py          # 18 automated unit and integration tests
├── .env.example                  # Template configuration file
├── .gitignore                    # Git exclusion rules
├── requirements.txt              # Production and testing dependencies
├── run.py                        # Convenient application launcher
└── README.md                     # Comprehensive project documentation
```

---

## 📋 Prerequisites

Before installing the application, ensure you have:
- **Python 3.10+** (Python 3.13 or 3.14 recommended)
- **Git** (for version control)
- *(Optional)* **Ollama** (if you wish to enable the local conversational LLM)

---

## 🚀 Installation & Setup

### Step 1: Clone or Navigate to the Repository
```bash
git clone <your-repository-url>
cd "EduSphere AI"
```

### Step 2: Create and Activate a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
py -3.13 -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example `.env` file:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

The defaults in `.env` are ready for local development:
```ini
APP_NAME="EduSphere AI"
PORT=8000
HOST="127.0.0.1"
DATABASE_URL="sqlite:///./edusphere.db"
OLLAMA_BASE_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="llama3.2"
```

---

## 🏃 Running the Application

### Option A: Using the Launcher Script (Recommended)
```bash
python run.py
```

### Option B: Using Uvicorn Directly
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once running:
- **Web Interface:** Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.
- **Interactive Swagger Docs:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **Alternative ReDoc UI:** Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## 🔌 API Documentation & Mandatory Endpoints

Every endpoint returns structured JSON, enforces strict validation, and adheres to standard HTTP status codes:

| HTTP Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/students` | Register a new student record | `201 Created`, `400`, `409 Conflict`, `422` |
| `GET` | `/students` | List, search, filter, and paginate students | `200 OK` |
| `GET` | `/students/{student_id}` | Retrieve a specific student profile | `200 OK`, `404 Not Found` |
| `PUT` | `/students/{student_id}` | Replace/update a student's full details | `200 OK`, `404 Not Found`, `422` |
| `PATCH` | `/students/{student_id}` | Partially update specific student fields | `200 OK`, `404 Not Found`, `422` |
| `DELETE` | `/students/{student_id}` | Permanently delete a student record | `200 OK`, `404 Not Found` |
| `GET` | `/students/stats/summary` | Aggregate dashboard KPI metrics | `200 OK` |
| `GET` | `/students/meta/courses` | List all distinct courses in the system | `200 OK` |
| `POST` | `/api/ai/chat` | Ask the grounded AI assistant a question | `200 OK`, `500` |
| `GET` | `/api/ai/status` | Check local Ollama connectivity and models | `200 OK` |
| `GET` | `/health` | System health check and record count | `200 OK` |

---

## 💡 Example API Requests & Responses

### 1. Create a Student (`POST /students`)

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU-2025-015",
    "full_name": "Kavya Menon",
    "date_of_birth": "2005-11-20",
    "email": "kavya.menon@example.com",
    "phone": "+91 9876543219",
    "course": "Artificial Intelligence",
    "address": "77 Palm Grove, Bengaluru",
    "enrollment_date": "2025-08-01"
  }'
```

**Response (`201 Created`):**
```json
{
  "id": 11,
  "student_id": "STU-2025-015",
  "full_name": "Kavya Menon",
  "date_of_birth": "2005-11-20",
  "email": "kavya.menon@example.com",
  "phone": "+91 9876543219",
  "course": "Artificial Intelligence",
  "address": "77 Palm Grove, Bengaluru",
  "enrollment_date": "2025-08-01",
  "created_at": "2026-10-15T10:15:00.000000Z",
  "updated_at": "2026-10-15T10:15:00.000000Z"
}
```

---

### 2. Search and Filter Students (`GET /students`)

**Request:**
```bash
curl "http://127.0.0.1:8000/students?search=Aarav&course=Computer%20Science"
```

**Response (`200 OK`):**
```json
{
  "total": 1,
  "page": 1,
  "limit": 20,
  "total_pages": 1,
  "items": [
    {
      "id": 1,
      "student_id": "STU-2025-001",
      "full_name": "Aarav Sharma",
      "date_of_birth": "2004-05-15",
      "email": "aarav.sharma@example.com",
      "phone": "+91 9876543210",
      "course": "Computer Science",
      "address": "42 Tech Boulevard, Koramangala, Bangalore",
      "enrollment_date": "2025-08-01",
      "created_at": "2026-10-15T10:00:00.000000Z",
      "updated_at": "2026-10-15T10:00:00.000000Z"
    }
  ]
}
```

---

### 3. Partial Update (`PATCH /students/{student_id}`)

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-2025-015" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91 9999888877"
  }'
```

**Response (`200 OK`):**
```json
{
  "id": 11,
  "student_id": "STU-2025-015",
  "full_name": "Kavya Menon",
  "date_of_birth": "2005-11-20",
  "email": "kavya.menon@example.com",
  "phone": "+91 9999888877",
  "course": "Artificial Intelligence",
  "address": "77 Palm Grove, Bengaluru",
  "enrollment_date": "2025-08-01",
  "created_at": "2026-10-15T10:15:00.000000Z",
  "updated_at": "2026-10-15T10:18:22.000000Z"
}
```

---

### 4. Delete Student (`DELETE /students/{student_id}`)

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-2025-015"
```

**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Student 'Kavya Menon' (ID: STU-2025-015) has been permanently deleted.",
  "student_id": "STU-2025-015"
}
```

---

### 5. Ask AI Assistant (`POST /api/ai/chat`)

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which students were born after 2005?"
  }'
```

**Response (`200 OK`):**
```json
{
  "query": "Which students were born after 2005?",
  "answer": "### Students born after 2005 (3 found):\n- **Diya Patel** (ID: `STU-2025-002`, DOB: 2006-03-22, Course: Artificial Intelligence)\n- **Ananya Iyer** (ID: `STU-2025-004`, DOB: 2006-08-14, Course: Computer Science)\n- **Sneha Kulkarni** (ID: `STU-2025-008`, DOB: 2007-02-10, Course: Data Science)",
  "source": "grounded_rules",
  "model": null,
  "ollama_available": false,
  "suggestions": [
    "How many students are registered?",
    "Show students enrolled in Computer Science.",
    "Which students were born after 2005?",
    "Summarize the student distribution by course."
  ]
}
```

---

## 🤖 Optional AI Assistant (Ollama Integration)

The application includes a hybrid AI assistant designed with **strict grounding**:
1. When a user asks a question, the backend retrieves verified data from SQLite using predefined SQLAlchemy functions (no unrestricted raw SQL).
2. If **Ollama** is running locally, it passes the verified database context to the model (`llama3.2` or any installed model) to formulate a friendly, conversational markdown response.
3. If Ollama is **not running**, the application automatically falls back to its **Deterministic Grounded Engine**, giving 100% accurate database answers without failing or throwing errors.

### Enabling Ollama Locally:
1. Download Ollama from [ollama.ai](https://ollama.ai) and install it.
2. Open a terminal and run your desired model:
   ```bash
   ollama run llama3.2
   ```
3. Refresh the EduSphere web interface — the AI status badge will immediately turn **Green ("Ollama Online")**!

---

## 🧪 Running the Automated Test Suite

The project includes an isolated test suite running against an in-memory SQLite database.

To run all 18 automated tests:
```bash
pytest -v
```

### Verified Test Cases:
- `test_create_student_success`: Validates record creation and response schema.
- `test_create_student_duplicate_id_fails`: Enforces `409 Conflict` on duplicate ID.
- `test_create_student_missing_contact_fails`: Verifies that either email or phone is required.
- `test_create_student_invalid_email_fails`: Validates email regex pattern.
- `test_create_student_future_dob_fails`: Ensures date of birth cannot be in the future.
- `test_list_students_and_pagination`: Tests pagination (`skip`, `limit`, `total_pages`).
- `test_list_students_search_by_name_and_id`: Tests search across names and IDs.
- `test_list_students_filter_by_course`: Validates course filtering logic.
- `test_get_student_by_id_success`: Fetches single record.
- `test_get_student_by_id_not_found`: Verifies `404 Not Found` for missing IDs.
- `test_put_update_student_full`: Tests complete record update.
- `test_patch_update_student_partial`: Tests partial updates while preserving other fields.
- `test_delete_student_success`: Verifies record deletion.
- `test_delete_student_not_found`: Enforces `404 Not Found` on deleting nonexistent records.
- `test_sqlite_persistence_across_sessions`: Closes and re-opens SQLite database file to verify data persists across restarts.
- `test_ai_assistant_grounded_response`: Verifies natural language intent parsing and data grounding.
- `test_ai_status_endpoint`: Tests AI connectivity check.
- `test_dashboard_stats_summary`: Tests KPI aggregation calculations.

---

## ❓ Troubleshooting & Common Questions

### 1. Port 8000 is already in use
Change the port in `.env` or run:
```bash
uvicorn app.main:app --port 8080 --reload
```

### 2. How can I reset the database to sample records?
Click the **Reset Sample Data** button in the dashboard header, or make a `POST` request:
```bash
curl -X POST "http://127.0.0.1:8000/api/seed?reset=true"
```

### 3. Will student records disappear if I restart the server?
**No.** All records are saved in the SQLite file `edusphere.db` in your workspace directory and persist indefinitely.

---

## 🎓 Internship Submission Notes

This project was developed for the **Python/AI-ML Internship at EWB Edu Tech Pvt. Ltd.**
- **Applicant:** Hardik
- **Core Competencies Demonstrated:**
  - RESTful API design using modern Python and FastAPI.
  - Relational database schema design and ORM querying using SQLAlchemy.
  - Strict input validation using Pydantic v2.
  - Responsive, accessible front-end development using HTML, CSS, and vanilla JS.
  - Grounded AI retrieval-augmented synthesis and integration with Ollama.
  - Test-driven development with Pytest.

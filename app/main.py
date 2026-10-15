from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db
from app.routers import students, ai
from app.seed import seed_database
from app import crud

settings = get_settings()

# Setup lifespan for startup database table creation and initial seed
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables are created in SQLite
    Base.metadata.create_all(bind=engine)
    # Seed initial realistic fictional records if database is empty
    seed_database()
    yield

app = FastAPI(
    title="EduSphere AI",
    description=(
        "### EduSphere AI — Smart Student Management System\n\n"
        "A robust, modern student management platform built with FastAPI, SQLAlchemy, SQLite, "
        "and an optional AI Assistant with Ollama integration.\n\n"
        "Developed for the Python/AI-ML Internship at EWB Edu Tech Pvt. Ltd."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "img").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


from fastapi.encoders import jsonable_encoder

# Custom validation error handler for friendly, readable messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"] if loc != "body")
        msg = err["msg"]
        errors.append(f"{field}: {msg}" if field else msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation failed for student data.",
            "errors": errors,
            "details": jsonable_encoder(exc.errors())
        }
    )


# Include API Routers
app.include_router(students.router)
app.include_router(ai.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_home(request: Request):
    """Serves the modern frontend dashboard."""
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint providing DB connectivity and student stats."""
    count = crud.ai_query_total_students(db)["total_students"]
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "sqlite_connected",
        "total_records": count
    }


@app.post("/api/seed", tags=["System"])
def reseed_data(reset: bool = False, db: Session = Depends(get_db)):
    """Seed or reset sample student data for testing and demonstration."""
    total = seed_database(db=db, force_reset=reset)
    return {
        "status": "success",
        "message": f"Database {'reset and ' if reset else ''}seeded with sample records.",
        "total_students": total
    }

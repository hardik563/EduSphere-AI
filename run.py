import sys
import uvicorn
from app.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print("=" * 65)
    print("  EduSphere AI — Smart Student Management System")
    print(f"  Running on: http://{settings.HOST}:{settings.PORT}")
    print(f"  Interactive API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  ReDoc Documentation: http://{settings.HOST}:{settings.PORT}/redoc")
    print("=" * 65)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

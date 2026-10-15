from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AIChatRequest, AIChatResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Ask EduSphere AI Assistant",
    description="Processes a natural language query grounded strictly in SQLite student records."
)
async def chat_with_assistant(
    req: AIChatRequest,
    db: Session = Depends(get_db)
):
    try:
        response = await ai_service.answer_question(req.message, db)
        return AIChatResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI query processing error: {str(e)}"
        )


@router.get(
    "/status",
    summary="Check Ollama availability",
    description="Checks whether the local Ollama server is running and lists accessible models."
)
async def get_ai_status():
    is_available, models, err_msg = await ai_service.check_ollama_status()
    return {
        "ollama_available": is_available,
        "base_url": ai_service.base_url,
        "configured_model": ai_service.model,
        "installed_models": models,
        "error_message": err_msg,
        "mode": "ollama_active" if is_available else "grounded_rules_fallback"
    }

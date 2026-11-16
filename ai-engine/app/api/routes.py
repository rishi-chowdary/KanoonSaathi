from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/internal")


@router.get("/health")
def internal_health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "provider": settings.llm_provider,
        "tesseract_available": settings.tesseract_available,
    }

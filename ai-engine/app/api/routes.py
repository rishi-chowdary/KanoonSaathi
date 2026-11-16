from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings
from app.schemas.extraction import ExtractionResponse, ExtractionErrorResponse
from app.services.extractor import process_document, ExtractionException

router = APIRouter()


@router.get("/internal/health")
@router.get("/health/internal")
def internal_health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "provider": settings.llm_provider,
        "tesseract_available": settings.tesseract_available,
    }


@router.post(
    "/internal/extract",
    response_model=ExtractionResponse,
    responses={400: {"model": ExtractionErrorResponse}},
)
@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={400: {"model": ExtractionErrorResponse}},
)
async def extract_document(file: UploadFile = File(...)):
    filename = file.filename or "document.pdf"
    content = await file.read()

    try:
        result = process_document(filename, content)
        return result
    except ExtractionException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"code": e.code, "detail": e.detail},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"code": "INTERNAL_ERROR", "detail": f"unexpected error: {str(e)}"},
        )

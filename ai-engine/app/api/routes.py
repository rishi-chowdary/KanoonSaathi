from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.config import settings
from app.schemas.extraction import ExtractionResponse, ExtractionErrorResponse
from app.schemas.summary import DocumentSummaryRequest, DocumentSummaryResponse
from app.services.extractor import process_document, ExtractionException
from app.services.summary_service import analyze_document_summary
from app.providers import get_llm_provider

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


@router.post(
    "/internal/analyze/summary",
    response_model=DocumentSummaryResponse,
    responses={400: {"model": ExtractionErrorResponse}},
)
@router.post(
    "/analyze/summary",
    response_model=DocumentSummaryResponse,
    responses={400: {"model": ExtractionErrorResponse}},
)
async def analyze_summary(request: DocumentSummaryRequest):
    provider = get_llm_provider()
    try:
        summary = await analyze_document_summary(
            document_id=request.document_id,
            pages=request.pages,
            chunks=request.chunks,
            provider=provider,
        )
        return summary
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"code": "SUMMARY_GENERATION_FAILED", "detail": str(e)},
        )

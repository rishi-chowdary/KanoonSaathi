import logging
import sys
import time
from fastapi import Depends, FastAPI, Request
from app.api.deps import verify_internal_api_key
from app.api.routes import router as internal_router
from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ai-engine")

app = FastAPI(
    title="LexiLegal AI Engine",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "tesseract_available": settings.tesseract_available,
    }


# All internal endpoints require X-Internal-Api-Key
app.include_router(
    internal_router,
    dependencies=[Depends(verify_internal_api_key)],
)

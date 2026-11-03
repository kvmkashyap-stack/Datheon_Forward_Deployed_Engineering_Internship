
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.middleware import SecurityAndMetricsMiddleware
from app.metrics import metrics_response
from app.schemas import GenerateRequest, GenerateResponse
from app.services.ai_service import AIService, record_token_usage


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production-oriented AI integration microservice",
    lifespan=lifespan,
)

app.add_middleware(SecurityAndMetricsMiddleware)


@app.get("/", tags=["service"])
def root():
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "status": "running",
    }


@app.get("/health/live", tags=["health"])
def liveness():
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def readiness():
    return {"status": "ready"}


@app.get("/health", tags=["health"], include_in_schema=False)
def health():
    return {"status": "healthy"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    if not settings.metrics_enabled:
        return JSONResponse(
            status_code=404,
            content={"detail": "Metrics are disabled"},
        )

    return metrics_response()


@app.post(
    "/api/v1/generate",
    response_model=GenerateResponse,
    tags=["AI"],
)
def generate(request: GenerateRequest):
    result = AIService().generate(request.prompt)
    record_token_usage(result)

    return GenerateResponse(
        answer=result.answer,
        provider=result.provider,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )

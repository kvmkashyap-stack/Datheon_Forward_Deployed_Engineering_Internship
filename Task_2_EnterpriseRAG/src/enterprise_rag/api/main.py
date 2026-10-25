
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status

from enterprise_rag.api.dependencies import get_pipeline, resolve_user
from enterprise_rag.api.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
)
from enterprise_rag.config import settings
from enterprise_rag.ingestion.service import ingest_pdf
from enterprise_rag.models import ClearanceLevel

MAX_PDF_SIZE = 20 * 1024 * 1024  # 20 MB

app = FastAPI(
    title=settings.app_name,
    description="Enterprise RAG with PDF upload, RBAC, reranking, and citations.",
    version="0.2.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", app_name=settings.app_name)


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    classification: str = Form(...),
) -> UploadResponse:
    """Ingest a PDF into the vector store for the local demo."""

    filename = Path(file.filename or "").name

    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a file with a .pdf extension.",
        )

    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="Tenant ID cannot be empty.")

    try:
        clearance = ClearanceLevel[classification.strip().upper()]
    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail="Classification must be public, internal, confidential, or restricted.",
        ) from exc

    content = await file.read(MAX_PDF_SIZE + 1)

    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 20 MB upload limit.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF.",
        )

    try:
        with TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / filename
            pdf_path.write_bytes(content)

            result = ingest_pdf(
                file_path=pdf_path,
                tenant_id=tenant_id.strip(),
                classification=clearance,
            )

        return UploadResponse(**result)

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest) -> QueryResponse:
    try:
        user = resolve_user(request.user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown demo user ID.",
        ) from exc

    try:
        pipeline = get_pipeline()
        result = pipeline.ask(
            question=request.question,
            user=user,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return QueryResponse(**result)

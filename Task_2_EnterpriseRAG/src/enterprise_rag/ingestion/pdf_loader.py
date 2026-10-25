from pathlib import Path

import pymupdf
from langchain_core.documents import Document

from enterprise_rag.models import ClearanceLevel


def load_pdf(
    file_path: str | Path,
    tenant_id: str,
    classification: ClearanceLevel,
    source_id: str | None = None,
) -> list[Document]:
    """Load PDF pages while preserving original 1-based page numbers."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension.")

    if not tenant_id.strip():
        raise ValueError("tenant_id cannot be empty.")

    documents: list[Document] = []
    resolved_source_id = source_id or path.stem

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            page_text = page.get_text("text").strip()

            if not page_text:
                continue

            documents.append(
                Document(
                    page_content=page_text,
                    metadata={
                        "tenant_id": tenant_id,
                        "classification": classification.name.lower(),
                        "classification_level": int(classification),
                        "source_id": resolved_source_id,
                        "source_name": path.name,
                        "page_number": page_number,
                    },
                )
            )

    return documents

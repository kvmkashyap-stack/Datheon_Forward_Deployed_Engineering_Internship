
from pathlib import Path

from enterprise_rag.ingestion.chunker import split_documents
from enterprise_rag.ingestion.pdf_loader import load_pdf
from enterprise_rag.models import ClearanceLevel
from enterprise_rag.retrieval.embeddings import get_embeddings
from enterprise_rag.retrieval.vector_store import (
    get_vector_store,
    index_documents,
)


def ingest_pdf(
    file_path: str | Path,
    tenant_id: str,
    classification: ClearanceLevel,
    source_id: str | None = None,
) -> dict[str, int | str]:
    """Extract, chunk, embed, and index a PDF with access-control metadata."""

    path = Path(file_path)

    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id cannot be empty.")

    # Extract one document per non-empty PDF page.
    pages = load_pdf(
        file_path=path,
        tenant_id=tenant_id.strip(),
        classification=classification,
        source_id=source_id,
    )

    if not pages:
        raise ValueError(
            f"No extractable text found in {path.name}. "
            "If this is a scanned PDF, OCR is required."
        )

    # Split each page while retaining source and page metadata.
    chunks = split_documents(pages)

    if not chunks:
        raise ValueError(f"No text chunks were produced for {path.name}.")

    # Create embeddings and persist chunks to ChromaDB.
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    indexed_count = index_documents(vector_store, chunks)

    return {
        "source": path.name,
        "pages_extracted": len(pages),
        "chunks_created": len(chunks),
        "chunks_indexed": indexed_count,
    }


from datetime import date
from pathlib import Path

from legacyai.chunking import DocumentChunk, chunk_document
from legacyai.config import DEFAULT_BATCH_SIZE
from legacyai.extractors.csv_extractor import extract_csv
from legacyai.extractors.markdown_extractor import extract_markdown
from legacyai.extractors.pdf_extractor import extract_pdf
from legacyai.metadata import build_metadata
from legacyai.models import AccessTier, DocumentMetadata, ExtractedDocument
from legacyai.vector_store import VectorStore


EXTRACTORS = {
    ".pdf": extract_pdf,
    ".csv": extract_csv,
    ".md": extract_markdown,
    ".markdown": extract_markdown,
}


def extract_file(
    file_path: str | Path,
    metadata: DocumentMetadata,
) -> list[ExtractedDocument]:
    """Select the appropriate extractor based on file extension."""

    path = Path(file_path)
    extractor = EXTRACTORS.get(path.suffix.lower())

    if extractor is None:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    return extractor(path, metadata)


def ingest_file(
    file_path: str | Path,
    department: str,
    access_tier: AccessTier,
    document_date: date,
    vector_store: VectorStore | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, int]:
    """Extract, chunk, and ingest one source file."""

    metadata = build_metadata(
        department=department,
        access_tier=access_tier,
        document_date=document_date,
    )

    documents = extract_file(file_path, metadata)

    chunks = [
        chunk
        for document in documents
        for chunk in chunk_document(document)
    ]

    store = vector_store if vector_store is not None else VectorStore()
    stored_count = store.add_chunks(chunks, batch_size=batch_size)

    return {
        "documents_extracted": len(documents),
        "chunks_created": len(chunks),
        "chunks_stored": stored_count,
    }


def ingest_directory(
    directory: str | Path,
    department: str,
    access_tier: AccessTier,
    document_date: date,
    vector_store: VectorStore | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, int]:
    """Extract all supported files and ingest chunks in shared batches."""

    root = Path(directory)

    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found: {root}")

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    metadata = build_metadata(
        department=department,
        access_tier=access_tier,
        document_date=document_date,
    )

    supported_files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in EXTRACTORS
    )

    all_chunks: list[DocumentChunk] = []
    documents_extracted = 0

    for path in supported_files:
        documents = extract_file(path, metadata)
        documents_extracted += len(documents)

        for document in documents:
            all_chunks.extend(chunk_document(document))

    store = vector_store if vector_store is not None else VectorStore()

    stored_count = store.add_chunks(
        all_chunks,
        batch_size=batch_size,
    )

    return {
        "files_processed": len(supported_files),
        "documents_extracted": documents_extracted,
        "chunks_created": len(all_chunks),
        "chunks_stored": stored_count,
    }

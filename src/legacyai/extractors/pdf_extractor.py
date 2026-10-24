from pathlib import Path
import pymupdf
from legacyai.models import DocumentMetadata, ExtractedDocument


def extract_pdf(
    file_path: str | Path,
    metadata: DocumentMetadata,
) -> list[ExtractedDocument]:
    """Extract non-empty pages from a PDF as normalized documents."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.name}")

    documents: list[ExtractedDocument] = []

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            content = page.get_text("text").strip()

            if not content:
                continue

            documents.append(
                ExtractedDocument(
                    document_id=f"{path.stem}-page-{page_number}",
                    source_path=str(path.resolve()),
                    source_type="pdf",
                    content=content,
                    metadata=metadata,
                )
            )

    return documents

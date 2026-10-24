from dataclasses import dataclass
from legacyai.config import CHUNK_OVERLAP, CHUNK_SIZE
from legacyai.models import DocumentMetadata, ExtractedDocument


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    source_path: str
    source_type: str
    content: str
    metadata: DocumentMetadata
    chunk_index: int


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if chunk_overlap is None:
        chunk_overlap = min(CHUNK_OVERLAP, max(0, chunk_size - 1))

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between 0 and chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer a nearby paragraph or sentence boundary.
        if end < len(text):
            boundary = max(
                text.rfind("\n\n", start, end),
                text.rfind(". ", start, end),
                text.rfind(" ", start, end),
            )

            if boundary > start + chunk_size // 2:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = max(start + 1, end - chunk_overlap)

        # Prevent a split from repeatedly stopping at the same boundary.
        start = next_start

    return chunks


def chunk_document(
    document: ExtractedDocument,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int | None = None,
) -> list[DocumentChunk]:
    """Split a document and preserve its metadata."""

    contents = split_text(document.content, chunk_size, chunk_overlap)

    return [
        DocumentChunk(
            chunk_id=f"{document.document_id}-chunk-{index}",
            document_id=document.document_id,
            source_path=document.source_path,
            source_type=document.source_type,
            content=content,
            metadata=document.metadata,
            chunk_index=index,
        )
        for index, content in enumerate(contents)
    ]
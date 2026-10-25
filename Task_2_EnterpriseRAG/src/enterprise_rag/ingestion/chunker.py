from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from enterprise_rag.config import settings


def split_documents(documents: list[Document]) -> list[Document]:
    """Split page-level documents while preserving source and page metadata."""

    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        metadata = chunk.metadata

        required_fields = (
            "tenant_id",
            "classification",
            "classification_level",
            "source_id",
            "source_name",
            "page_number",
        )

        missing = [field for field in required_fields if field not in metadata]
        if missing:
            raise ValueError(
                f"Chunk is missing required security or citation metadata: {missing}"
            )

        if not isinstance(metadata["page_number"], int) or metadata["page_number"] < 1:
            raise ValueError("Each chunk must have a valid 1-based page_number.")

    return chunks

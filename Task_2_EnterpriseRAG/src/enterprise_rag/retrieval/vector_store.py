from hashlib import sha256
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from enterprise_rag.config import settings


def _chunk_id(document: Document) -> str:
    """Generate a stable ID from source, page, position, and chunk content."""

    metadata = document.metadata

    identity = "|".join(
        [
            str(metadata["tenant_id"]),
            str(metadata["source_id"]),
            str(metadata["page_number"]),
            str(metadata.get("start_index", 0)),
            document.page_content,
        ]
    )

    return sha256(identity.encode("utf-8")).hexdigest()


def get_vector_store(embeddings: HuggingFaceEmbeddings) -> Chroma:
    """Open or create the persistent ChromaDB collection."""

    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )


def index_documents(
    vector_store: Chroma,
    documents: list[Document],
) -> int:
    """Validate metadata and add or update chunks in ChromaDB."""

    if not documents:
        return 0

    required_fields = {
        "tenant_id",
        "classification",
        "classification_level",
        "source_id",
        "source_name",
        "page_number",
    }

    ids: list[str] = []

    for document in documents:
        missing = required_fields - document.metadata.keys()
        if missing:
            raise ValueError(f"Missing required document metadata: {sorted(missing)}")

        if not document.page_content.strip():
            raise ValueError("Cannot index an empty document chunk.")

        if not isinstance(document.metadata["classification_level"], int):
            raise ValueError("classification_level must be an integer.")

        if not isinstance(document.metadata["page_number"], int):
            raise ValueError("page_number must be an integer.")

        if document.metadata["page_number"] < 1:
            raise ValueError("page_number must be 1 or greater.")

        ids.append(_chunk_id(document))

    vector_store.add_documents(documents=documents, ids=ids)
    return len(documents)

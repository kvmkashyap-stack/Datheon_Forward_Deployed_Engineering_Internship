from pathlib import Path
import chromadb
from legacyai.chunking import DocumentChunk
from legacyai.config import CHROMA_DIR, COLLECTION_NAME
from legacyai.embeddings import embed_texts
from legacyai.metadata import to_vector_metadata


class VectorStore:
    """Manage persistent vector storage and batch ingestion."""

    def __init__(
        self,
        persist_directory: str | Path = CHROMA_DIR,
        collection_name: str = COLLECTION_NAME,
    ) -> None:
        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        batch_size: int = 100,
    ) -> int:
        """Embed and upsert chunks in batches; return count processed."""

        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        total_processed = 0

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]

            embeddings = embed_texts(
                [chunk.content for chunk in batch]
            )

            self.collection.upsert(
                ids=[chunk.chunk_id for chunk in batch],
                documents=[chunk.content for chunk in batch],
                embeddings=embeddings,
                metadatas=[
                    {
                        **to_vector_metadata(chunk.metadata),
                        "document_id": chunk.document_id,
                        "source_path": chunk.source_path,
                        "source_type": chunk.source_type,
                        "chunk_index": chunk.chunk_index,
                    }
                    for chunk in batch
                ],
            )

            total_processed += len(batch)

        return total_processed

    def count(self) -> int:
        """Return the number of chunks currently stored."""

        return self.collection.count()

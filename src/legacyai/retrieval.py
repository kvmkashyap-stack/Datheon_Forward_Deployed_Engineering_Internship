
from datetime import date
from typing import Any

from legacyai.embeddings import embed_query
from legacyai.metadata import build_where_filter
from legacyai.models import AccessTier
from legacyai.vector_store import VectorStore


def search_documents(
    query: str,
    top_k: int = 5,
    department: str | None = None,
    access_tier: AccessTier | None = None,
    document_date: date | None = None,
    vector_store: VectorStore | None = None,
) -> list[dict[str, Any]]:
    """Search stored chunks using semantic similarity and filters."""

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    store = vector_store or VectorStore()

    where_filter = build_where_filter(
        department=department,
        access_tier=access_tier,
        document_date=document_date,
    )

    results = store.collection.query(
        query_embeddings=[embed_query(query)],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    matches: list[dict[str, Any]] = []

    ids = results["ids"][0]
    documents = results["documents"][0] or []
    metadatas = results["metadatas"][0] or []
    distances = results["distances"][0] or []

    for index, chunk_id in enumerate(ids):
        matches.append(
            {
                "chunk_id": chunk_id,
                "content": documents[index],
                "metadata": metadatas[index],
                "distance": distances[index],
            }
        )

    return matches

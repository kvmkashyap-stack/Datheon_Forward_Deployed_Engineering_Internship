from functools import lru_cache
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from enterprise_rag.config import settings


@lru_cache(maxsize=1)
def _load_cross_encoder() -> CrossEncoder:
    """Load the reranking model once per process."""

    return CrossEncoder(
        settings.reranker_model,
        device="cpu",
    )


def rerank_documents(
    query: str,
    documents: list[Document],
    top_k: int | None = None,
) -> list[Document]:
    """Sort already-authorized documents by cross-encoder relevance."""

    if not query.strip() or not documents:
        return []

    if top_k is None:
        top_k = settings.rerank_top_k

    if top_k < 1:
        raise ValueError("top_k must be greater than zero.")

    model = _load_cross_encoder()

    pairs = [
        (query, document.page_content)
        for document in documents
    ]
    scores = model.predict(pairs)

    ranked = sorted(
        zip(documents, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    results: list[Document] = []

    for document, score in ranked[:top_k]:
        # Return a copy so the original indexed metadata remains unchanged.
        result = Document(
            page_content=document.page_content,
            metadata={
                **document.metadata,
                "rerank_score": float(score),
            },
        )
        results.append(result)

    return results

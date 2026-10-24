from functools import lru_cache
from sentence_transformers import SentenceTransformer

from legacyai.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once per process."""

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate normalized embeddings for a batch of texts."""

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Cannot embed empty text")

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Generate an embedding for a single search query."""

    if not query.strip():
        raise ValueError("Query cannot be empty")

    return embed_texts([query])[0]

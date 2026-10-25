from langchain_huggingface import HuggingFaceEmbeddings
from enterprise_rag.config import settings


def get_embeddings() -> HuggingFaceEmbeddings:
    """Create the configured sentence-transformer embedding model."""

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

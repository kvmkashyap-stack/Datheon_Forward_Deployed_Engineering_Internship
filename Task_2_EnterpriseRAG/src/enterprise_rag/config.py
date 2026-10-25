
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EnterpriseRAG"
    app_env: str = "development"

    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "enterprise_documents"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    retrieval_top_k: int = 10
    rerank_top_k: int = 4

    chunk_size: int = 800
    chunk_overlap: int = 120

    # Google Gemini configuration
    google_api_key: str = ""
    google_model: str = "gemini-2.5-flash"
    google_temperature: float = 0.0


settings = Settings()

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "legacy_documents"

EMBEDDING_MODEL_NAME = os.getenv(
    "LEGACYAI_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

DEFAULT_BATCH_SIZE = 100

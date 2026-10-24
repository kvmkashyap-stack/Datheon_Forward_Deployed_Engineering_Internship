from datetime import date

import pytest

from legacyai.chunking import DocumentChunk
from legacyai.models import DocumentMetadata
from legacyai.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(
        persist_directory=tmp_path / "chroma_db",
        collection_name="test_documents",
    )


@pytest.fixture
def sample_chunks():
    metadata = DocumentMetadata(
        department="Engineering",
        access_tier="internal",
        document_date=date(2026, 10, 24),
    )

    return [
        DocumentChunk(
            chunk_id="policy-1-chunk-0",
            document_id="policy-1",
            source_path="/data/policy.md",
            source_type="markdown",
            content="Employees receive annual leave.",
            metadata=metadata,
            chunk_index=0,
        ),
        DocumentChunk(
            chunk_id="policy-1-chunk-1",
            document_id="policy-1",
            source_path="/data/policy.md",
            source_type="markdown",
            content="Full-time employees are eligible.",
            metadata=metadata,
            chunk_index=1,
        ),
    ]


def test_vector_store_uses_cosine_similarity(vector_store):
    assert vector_store.collection.metadata["hnsw:space"] == "cosine"


def test_add_chunks_stores_documents_and_metadata(
    vector_store,
    sample_chunks,
    monkeypatch,
):
    monkeypatch.setattr(
        "legacyai.vector_store.embed_texts",
        lambda texts: [[0.1, 0.2, 0.3] for _ in texts],
    )

    stored_count = vector_store.add_chunks(sample_chunks, batch_size=2)

    assert stored_count == 2
    assert vector_store.count() == 2

    result = vector_store.collection.get(
        ids=["policy-1-chunk-0"],
        include=["documents", "metadatas"],
    )

    assert result["documents"][0] == "Employees receive annual leave."

    metadata = result["metadatas"][0]
    assert metadata["department"] == "engineering"
    assert metadata["access_tier"] == "internal"
    assert metadata["document_date"] == "2026-10-24"
    assert metadata["document_id"] == "policy-1"
    assert metadata["source_type"] == "markdown"
    assert metadata["chunk_index"] == 0


def test_add_chunks_processes_multiple_batches(
    vector_store,
    sample_chunks,
    monkeypatch,
):
    embedding_calls = []

    def fake_embed_texts(texts):
        embedding_calls.append(len(texts))
        return [[0.1, 0.2, 0.3] for _ in texts]

    monkeypatch.setattr(
        "legacyai.vector_store.embed_texts",
        fake_embed_texts,
    )

    result = vector_store.add_chunks(sample_chunks, batch_size=1)

    assert result == 2
    assert embedding_calls == [1, 1]
    assert vector_store.count() == 2


def test_upsert_updates_existing_chunk(
    vector_store,
    sample_chunks,
    monkeypatch,
):
    monkeypatch.setattr(
        "legacyai.vector_store.embed_texts",
        lambda texts: [[0.1, 0.2, 0.3] for _ in texts],
    )

    vector_store.add_chunks(sample_chunks[:1])

    updated_chunk = DocumentChunk(
        chunk_id="policy-1-chunk-0",
        document_id="policy-1",
        source_path="/data/policy.md",
        source_type="markdown",
        content="Updated leave policy.",
        metadata=sample_chunks[0].metadata,
        chunk_index=0,
    )

    vector_store.add_chunks([updated_chunk])

    assert vector_store.count() == 1

    result = vector_store.collection.get(
        ids=["policy-1-chunk-0"],
        include=["documents"],
    )

    assert result["documents"][0] == "Updated leave policy."


def test_invalid_batch_size_is_rejected(vector_store, sample_chunks):
    with pytest.raises(ValueError, match="batch_size must be positive"):
        vector_store.add_chunks(sample_chunks, batch_size=0)
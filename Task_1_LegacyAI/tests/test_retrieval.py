from datetime import date

import pytest

from legacyai.retrieval import search_documents


class FakeCollection:
    def __init__(self):
        self.query_arguments = None

    def query(self, **kwargs):
        self.query_arguments = kwargs

        return {
            "ids": [["policy-1-chunk-0"]],
            "documents": [["Employees receive annual leave."]],
            "metadatas": [
                [
                    {
                        "department": "hr",
                        "access_tier": "internal",
                        "document_date": "2026-10-24",
                    }
                ]
            ],
            "distances": [[0.12]],
        }


class FakeVectorStore:
    def __init__(self):
        self.collection = FakeCollection()


def test_search_returns_matching_chunks(monkeypatch):
    store = FakeVectorStore()

    monkeypatch.setattr(
        "legacyai.retrieval.embed_query",
        lambda query: [0.1, 0.2, 0.3],
    )

    results = search_documents(
        query="What is the annual leave policy?",
        top_k=3,
        vector_store=store,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "policy-1-chunk-0"
    assert results[0]["content"] == "Employees receive annual leave."
    assert results[0]["distance"] == 0.12

    assert store.collection.query_arguments["n_results"] == 3
    assert store.collection.query_arguments["query_embeddings"] == [
        [0.1, 0.2, 0.3]
    ]


def test_search_applies_metadata_filters(monkeypatch):
    store = FakeVectorStore()

    monkeypatch.setattr(
        "legacyai.retrieval.embed_query",
        lambda query: [0.1, 0.2, 0.3],
    )

    search_documents(
        query="annual leave",
        department="HR",
        access_tier="internal",
        document_date=date(2026, 10, 24),
        vector_store=store,
    )

    assert store.collection.query_arguments["where"] == {
        "$and": [
            {"department": "hr"},
            {"access_tier": "internal"},
            {"document_date": "2026-10-24"},
        ]
    }


def test_search_rejects_empty_query():
    with pytest.raises(ValueError, match="Query cannot be empty"):
        search_documents(query="   ", vector_store=FakeVectorStore())


def test_search_rejects_nonpositive_top_k():
    with pytest.raises(ValueError, match="top_k must be positive"):
        search_documents(
            query="annual leave",
            top_k=0,
            vector_store=FakeVectorStore(),
        )


def test_search_without_filters_passes_none(monkeypatch):
    store = FakeVectorStore()

    monkeypatch.setattr(
        "legacyai.retrieval.embed_query",
        lambda query: [0.1, 0.2, 0.3],
    )

    search_documents(
        query="annual leave",
        vector_store=store,
    )

    assert store.collection.query_arguments["where"] is None
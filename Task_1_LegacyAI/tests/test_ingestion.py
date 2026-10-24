from datetime import date

import pytest

from legacyai.ingestion import (
    extract_file,
    ingest_directory,
    ingest_file,
)
from legacyai.models import DocumentMetadata


class FakeVectorStore:
    def __init__(self):
        self.received_chunks = []
        self.batch_sizes = []

    def add_chunks(self, chunks, batch_size=100):
        self.received_chunks.extend(chunks)
        self.batch_sizes.append(batch_size)
        return len(chunks)


def test_extract_file_selects_markdown_extractor(
    sample_markdown,
    sample_metadata,
):
    documents = extract_file(sample_markdown, sample_metadata)

    assert documents
    assert all(document.source_type == "markdown" for document in documents)


def test_extract_file_rejects_unsupported_format(
    tmp_path,
    sample_metadata,
):
    unsupported_file = tmp_path / "notes.txt"
    unsupported_file.write_text("Some text", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_file(unsupported_file, sample_metadata)


def test_ingest_file_extracts_chunks_and_stores_them(
    sample_markdown,
):
    store = FakeVectorStore()

    result = ingest_file(
        file_path=sample_markdown,
        department="HR",
        access_tier="internal",
        document_date=date(2026, 10, 24),
        vector_store=store,
        batch_size=25,
    )

    assert result["documents_extracted"] == 2
    assert result["chunks_created"] >= 2
    assert result["chunks_stored"] == result["chunks_created"]
    assert len(store.received_chunks) == result["chunks_created"]
    assert store.batch_sizes == [25]

    for chunk in store.received_chunks:
        assert chunk.metadata.department == "hr"
        assert chunk.metadata.access_tier == "internal"
        assert chunk.metadata.document_date == date(2026, 10, 24)


def test_ingest_directory_processes_supported_files(
    tmp_path,
    sample_metadata,
):
    markdown_dir = tmp_path / "markdown"
    csv_dir = tmp_path / "csv"

    markdown_dir.mkdir()
    csv_dir.mkdir()

    (markdown_dir / "policy.md").write_text(
        "# Policy\n\nEmployees receive annual leave.",
        encoding="utf-8",
    )
    (csv_dir / "employees.csv").write_text(
        "name,department\nAlice,Engineering\nBob,HR\n",
        encoding="utf-8",
    )
    (tmp_path / "ignore.txt").write_text(
        "This file should not be ingested.",
        encoding="utf-8",
    )

    store = FakeVectorStore()

    result = ingest_directory(
        directory=tmp_path,
        department="Engineering",
        access_tier="internal",
        document_date=date(2026, 10, 24),
        vector_store=store,
    )

    assert result["files_processed"] == 2
    assert result["documents_extracted"] == 3
    assert result["chunks_created"] >= 3
    assert result["chunks_stored"] == result["chunks_created"]


def test_ingest_directory_rejects_missing_directory(tmp_path):
    missing_directory = tmp_path / "does_not_exist"

    with pytest.raises(NotADirectoryError):
        ingest_directory(
            directory=missing_directory,
            department="HR",
            access_tier="internal",
            document_date=date(2026, 10, 24),
            vector_store=FakeVectorStore(),
        )
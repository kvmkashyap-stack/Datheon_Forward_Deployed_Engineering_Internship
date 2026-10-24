from legacyai.chunking import chunk_document, split_text
from legacyai.models import ExtractedDocument


def test_empty_text_returns_no_chunks():
    assert split_text("   ") == []


def test_short_text_returns_single_chunk():
    assert split_text("Hello LegacyAI", chunk_size=60, chunk_overlap=10) == [
        "Hello LegacyAI"
    ]


def test_long_text_creates_multiple_chunks():
    text = "alpha beta gamma delta epsilon " * 20

    chunks = split_text(
        text,
        chunk_size=60,
        chunk_overlap=10,
    )

    assert len(chunks) > 1
    assert all(chunks)


def test_invalid_chunk_configuration_raises_error():
    try:
        split_text("sample", chunk_size=10, chunk_overlap=10)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_chunk_preserves_metadata(sample_metadata):
    document = ExtractedDocument(
        document_id="policy-1",
        source_path="policy.md",
        source_type="markdown",
        content="Employee leave policy " * 20,
        metadata=sample_metadata,
    )

    chunks = chunk_document(
        document,
        chunk_size=60,
        chunk_overlap=10,
    )

    assert len(chunks) > 1
    assert chunks[0].document_id == "policy-1"
    assert chunks[0].metadata == sample_metadata
    assert chunks[0].chunk_index == 0

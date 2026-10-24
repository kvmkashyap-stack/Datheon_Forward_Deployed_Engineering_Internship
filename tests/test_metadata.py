from datetime import date

import pytest
from pydantic import ValidationError

from legacyai.metadata import (
    build_metadata,
    build_where_filter,
    to_vector_metadata,
)
from legacyai.models import DocumentMetadata


def test_build_metadata_normalizes_department():
    metadata = build_metadata(
        department="  Engineering  ",
        access_tier="internal",
        document_date=date(2026, 10, 24),
    )

    assert metadata.department == "engineering"
    assert metadata.access_tier == "internal"
    assert metadata.document_date == date(2026, 10, 24)


def test_vector_metadata_uses_string_values(sample_metadata):
    result = to_vector_metadata(sample_metadata)

    assert result == {
        "department": "hr",
        "access_tier": "internal",
        "document_date": "2026-10-24",
    }


def test_filter_returns_none_when_no_constraints():
    assert build_where_filter() is None


def test_filter_with_one_constraint():
    result = build_where_filter(department=" HR ")

    assert result == {"department": "hr"}


def test_filter_combines_multiple_constraints():
    result = build_where_filter(
        department="Engineering",
        access_tier="confidential",
        document_date=date(2026, 1, 15),
    )

    assert result == {
        "$and": [
            {"department": "engineering"},
            {"access_tier": "confidential"},
            {"document_date": "2026-01-15"},
        ]
    }


def test_empty_department_filter_raises_error():
    with pytest.raises(ValueError, match="Department cannot be empty"):
        build_where_filter(department="   ")


def test_invalid_access_tier_is_rejected():
    with pytest.raises(ValidationError):
        DocumentMetadata(
            department="engineering",
            access_tier="top-secret",
            document_date=date(2026, 10, 24),
        )
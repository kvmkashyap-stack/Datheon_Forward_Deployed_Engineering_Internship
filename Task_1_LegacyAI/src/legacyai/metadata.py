from datetime import date
from typing import Any
from legacyai.models import AccessTier, DocumentMetadata

def build_metadata(
    department: str,
    access_tier: AccessTier,
    document_date: date,
) -> DocumentMetadata:
    """Create validated metadata for an ingested document."""

    return DocumentMetadata(
        department=department,
        access_tier=access_tier,
        document_date=document_date,
    )


def to_vector_metadata(
    metadata: DocumentMetadata,
) -> dict[str, str]:
    """Convert metadata to ChromaDB-compatible scalar values."""

    return {
        "department": metadata.department,
        "access_tier": metadata.access_tier,
        "document_date": metadata.document_date.isoformat(),
    }


def build_where_filter(
    department: str | None = None,
    access_tier: AccessTier | None = None,
    document_date: date | None = None,
) -> dict[str, Any] | None:
    """Build a ChromaDB filter from supplied metadata constraints."""

    conditions: list[dict[str, Any]] = []

    if department is not None:
        normalized_department = department.strip().lower()

        if not normalized_department:
            raise ValueError("Department cannot be empty")

        conditions.append({"department": normalized_department})

    if access_tier is not None:
        conditions.append({"access_tier": access_tier})

    if document_date is not None:
        conditions.append(
            {"document_date": document_date.isoformat()}
        )

    if not conditions:
        return None

    if len(conditions) == 1:
        return conditions[0]

    return {"$and": conditions}

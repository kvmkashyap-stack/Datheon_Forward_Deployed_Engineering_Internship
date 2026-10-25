
from langchain_core.documents import Document

from enterprise_rag.models import ClearanceLevel, UserContext
from enterprise_rag.security.rbac import (
    build_rbac_filter,
    enforce_rbac,
    is_authorized,
)


def make_user(
    tenant_id: str = "tenant-alpha",
    clearance: ClearanceLevel = ClearanceLevel.INTERNAL,
) -> UserContext:
    return UserContext(
        user_id="test-user",
        tenant_id=tenant_id,
        clearance=clearance,
    )


def make_document(
    tenant_id: str = "tenant-alpha",
    classification: ClearanceLevel = ClearanceLevel.PUBLIC,
) -> Document:
    return Document(
        page_content="Test document content.",
        metadata={
            "tenant_id": tenant_id,
            "classification": classification.name.lower(),
            "classification_level": int(classification),
            "source_id": "test-document",
            "source_name": "test.pdf",
            "page_number": 1,
        },
    )


def test_user_can_access_document_within_clearance() -> None:
    user = make_user(clearance=ClearanceLevel.INTERNAL)
    document = make_document(classification=ClearanceLevel.INTERNAL)

    assert is_authorized(user, document.metadata)


def test_user_cannot_access_higher_clearance_document() -> None:
    user = make_user(clearance=ClearanceLevel.PUBLIC)
    document = make_document(classification=ClearanceLevel.CONFIDENTIAL)

    assert not is_authorized(user, document.metadata)


def test_user_cannot_access_another_tenant() -> None:
    user = make_user(tenant_id="tenant-alpha")
    document = make_document(tenant_id="tenant-beta")

    assert not is_authorized(user, document.metadata)


def test_enforce_rbac_removes_unauthorized_documents() -> None:
    user = make_user(clearance=ClearanceLevel.INTERNAL)

    documents = [
        make_document(classification=ClearanceLevel.PUBLIC),
        make_document(classification=ClearanceLevel.INTERNAL),
        make_document(classification=ClearanceLevel.RESTRICTED),
        make_document(tenant_id="tenant-beta"),
    ]

    authorized = enforce_rbac(user, documents)

    assert len(authorized) == 2
    assert all(is_authorized(user, doc.metadata) for doc in authorized)


def test_invalid_classification_is_denied() -> None:
    user = make_user()

    metadata = {
        "tenant_id": "tenant-alpha",
        "classification_level": 99,
    }

    assert not is_authorized(user, metadata)


def test_missing_classification_is_denied() -> None:
    user = make_user()

    metadata = {"tenant_id": "tenant-alpha"}

    assert not is_authorized(user, metadata)


def test_chroma_filter_contains_tenant_and_clearance() -> None:
    user = make_user(
        tenant_id="tenant-alpha",
        clearance=ClearanceLevel.CONFIDENTIAL,
    )

    metadata_filter = build_rbac_filter(user)

    assert "$and" in metadata_filter
    assert {"tenant_id": {"$eq": "tenant-alpha"}} in metadata_filter["$and"]
    assert {
        "classification_level": {"$lte": int(ClearanceLevel.CONFIDENTIAL)}
    } in metadata_filter["$and"]

from langchain_core.documents import Document
from enterprise_rag.models import ClearanceLevel, UserContext

def build_rbac_filter(user: UserContext) -> dict:
    """Build a ChromaDB metadata filter for tenant and clearance isolation."""

    return {
        "$and": [
            {"tenant_id": {"$eq": user.tenant_id}},
            {
                "classification_level": {
                    "$lte": int(user.clearance),
                }
            },
        ]
    }


def is_authorized(user: UserContext, metadata: dict) -> bool:
    """Check a document's metadata against the user's trusted permissions."""

    tenant_id = metadata.get("tenant_id")
    classification_level = metadata.get("classification_level")

    if tenant_id != user.tenant_id:
        return False

    if isinstance(classification_level, bool):
        return False

    if not isinstance(classification_level, int):
        return False

    try:
        classification = ClearanceLevel(classification_level)
    except ValueError:
        return False

    return classification <= user.clearance


def enforce_rbac(
    user: UserContext,
    documents: list[Document],
) -> list[Document]:
    """Remove unauthorized documents as a defense-in-depth check."""

    return [
        document
        for document in documents
        if is_authorized(user, document.metadata)
    ]
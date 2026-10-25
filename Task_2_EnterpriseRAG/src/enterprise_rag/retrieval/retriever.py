from langchain_chroma import Chroma
from langchain_core.documents import Document

from enterprise_rag.config import settings
from enterprise_rag.models import UserContext
from enterprise_rag.security.rbac import build_rbac_filter, enforce_rbac


class SecureRetriever:
    """Retrieve relevant documents subject to tenant isolation and RBAC."""

    def __init__(
        self,
        vector_store: Chroma,
        top_k: int | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.top_k = top_k or settings.retrieval_top_k

        if self.top_k < 1:
            raise ValueError("top_k must be greater than zero.")

    def retrieve(
        self,
        query: str,
        user: UserContext,
    ) -> list[Document]:
        """Return only authorized documents relevant to the query."""

        if not query or not query.strip():
            return []

        # Apply authorization inside the vector database search.
        metadata_filter = build_rbac_filter(user)

        candidates = self.vector_store.similarity_search(
            query=query.strip(),
            k=self.top_k,
            filter=metadata_filter,
        )

        # Defense in depth: never return unauthorized candidates downstream.
        authorized_documents = enforce_rbac(user, candidates)

        return authorized_documents

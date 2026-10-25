from functools import lru_cache
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

from enterprise_rag.config import settings
from enterprise_rag.models import ClearanceLevel, UserContext
from enterprise_rag.pipeline import EnterpriseRAGPipeline
from enterprise_rag.retrieval.embeddings import get_embeddings
from enterprise_rag.retrieval.vector_store import get_vector_store


# Local demonstration identities only.
# Replace this registry with a trusted identity provider before deployment.
USER_REGISTRY: dict[str, UserContext] = {
    "demo-public": UserContext(
        user_id="demo-public",
        tenant_id="tenant-alpha",
        clearance=ClearanceLevel.PUBLIC,
    ),
    "demo-internal": UserContext(
        user_id="demo-internal",
        tenant_id="tenant-alpha",
        clearance=ClearanceLevel.INTERNAL,
    ),
    "demo-confidential": UserContext(
        user_id="demo-confidential",
        tenant_id="tenant-alpha",
        clearance=ClearanceLevel.CONFIDENTIAL,
    ),
    "demo-restricted": UserContext(
        user_id="demo-restricted",
        tenant_id="tenant-alpha",
        clearance=ClearanceLevel.RESTRICTED,
    ),
    "demo-other-tenant": UserContext(
        user_id="demo-other-tenant",
        tenant_id="tenant-beta",
        clearance=ClearanceLevel.RESTRICTED,
    ),
}


def resolve_user(user_id: str) -> UserContext:
    """Resolve permissions from the server-side demo registry."""

    user = USER_REGISTRY.get(user_id)
    if user is None:
        raise ValueError("Unknown user ID.")

    return user


@lru_cache(maxsize=1)
def get_pipeline() -> EnterpriseRAGPipeline:
    """Create the RAG pipeline with the configured Gemini chat model."""

    if not settings.google_api_key.strip():
        raise RuntimeError(
            "Google Gemini API key is missing. "
            "Set GOOGLE_API_KEY in the project-root .env file."
        )

    embeddings = get_embeddings()
    vector_store: Chroma = get_vector_store(embeddings)

    llm = ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=settings.google_temperature,
        max_retries=2,
    )

    return EnterpriseRAGPipeline(
        vector_store=vector_store,
        llm=llm,
    )

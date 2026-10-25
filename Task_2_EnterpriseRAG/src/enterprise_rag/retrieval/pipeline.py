from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel

from enterprise_rag.config import settings
from enterprise_rag.generation.answer_generator import (
    ABSTENTION_MESSAGE,
    generate_answer,
)
from enterprise_rag.models import UserContext
from enterprise_rag.retrieval.query_rewriter import rewrite_query
from enterprise_rag.retrieval.reranker import rerank_documents
from enterprise_rag.retrieval.retriever import SecureRetriever


class EnterpriseRAGPipeline:
    """Orchestrate secure retrieval, reranking, and grounded generation."""

    def __init__(
        self,
        vector_store: Chroma,
        llm: BaseChatModel | None = None,
    ) -> None:
        self.retriever = SecureRetriever(
            vector_store=vector_store,
            top_k=settings.retrieval_top_k,
        )
        self.llm = llm

    def ask(self, question: str, user: UserContext) -> dict:
        """Answer a question using only the user's authorized documents."""

        if not question or not question.strip():
            return {
                "answer": "Please provide a non-empty question.",
                "citations": [],
                "retrieved_chunks": 0,
            }

        rewritten_query = rewrite_query(question)

        if not rewritten_query:
            return {
                "answer": "Please provide a non-empty question.",
                "citations": [],
                "retrieved_chunks": 0,
            }

        # RBAC is enforced inside the vector search and checked again afterward.
        authorized_documents = self.retriever.retrieve(
            query=rewritten_query,
            user=user,
        )

        if not authorized_documents:
            return {
                "answer": ABSTENTION_MESSAGE,
                "citations": [],
                "retrieved_chunks": 0,
            }

        # Only authorized documents are passed to the cross-encoder.
        ranked_documents = rerank_documents(
            query=rewritten_query,
            documents=authorized_documents,
            top_k=settings.rerank_top_k,
        )

        if not ranked_documents:
            return {
                "answer": ABSTENTION_MESSAGE,
                "citations": [],
                "retrieved_chunks": 0,
            }

        if self.llm is None:
            raise RuntimeError(
                "No LLM is configured. Configure a LangChain chat model "
                "before requesting generated answers."
            )

        answer = generate_answer(
            question=question,
            user=user,
            documents=ranked_documents,
            llm=self.llm,
        )

        citations = [
            {
                "source": document.metadata["source_name"],
                "page": document.metadata["page_number"],
            }
            for document in ranked_documents
        ]

        # Deduplicate citations while preserving order.
        unique_citations = list(
            {
                (citation["source"], citation["page"]): citation
                for citation in citations
            }.values()
        )

        return {
            "answer": answer,
            "citations": unique_citations,
            "retrieved_chunks": len(ranked_documents),
        }

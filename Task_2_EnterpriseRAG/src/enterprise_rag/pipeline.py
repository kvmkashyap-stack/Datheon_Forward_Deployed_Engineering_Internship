from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from enterprise_rag.conversation.intent_router import get_conversation_response

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
        if not question or not question.strip():
            return {
                "answer": "Please provide a non-empty question.",
                "citations": [],
                "retrieved_chunks": 0,
            }

        # Handle greetings and small talk without searching the vector store.
        conversation_response = get_conversation_response(question)
        if conversation_response is not None:
            return {
                "answer": conversation_response,
                "citations": [],
                "retrieved_chunks": 0,
            }

        query = rewrite_query(question)
        if not query:
            return {
                "answer": "Please provide a non-empty question.",
                "citations": [],
                "retrieved_chunks": 0,
            }

        documents = self.retriever.retrieve(query, user)

        if not documents:
            return {
                "answer": ABSTENTION_MESSAGE,
                "citations": [],
                "retrieved_chunks": 0,
            }

        ranked = rerank_documents(
            query,
            documents,
            top_k=settings.rerank_top_k,
        )

        if not ranked:
            return {
                "answer": ABSTENTION_MESSAGE,
                "citations": [],
                "retrieved_chunks": 0,
            }

        if self.llm is None:
            raise RuntimeError(
                "No LLM configured. Configure a LangChain chat model first."
            )

        answer = generate_answer(
            question=question,
            user=user,
            documents=ranked,
            llm=self.llm,
        )

        citations = list(
            dict.fromkeys(
                (
                    document.metadata["source_name"],
                    document.metadata["page_number"],
                )
                for document in ranked
            )
        )

        return {
            "answer": answer,
            "citations": [
                {"source": source, "page": page}
                for source, page in citations
            ],
            "retrieved_chunks": len(ranked),
        }
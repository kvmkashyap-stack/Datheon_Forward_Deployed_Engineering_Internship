# Datheon — Forward Deployed Engineering Internship

A collection of four engineering projects focused on enterprise document ingestion, secure retrieval-augmented generation, autonomous business-tool orchestration, and production-oriented AI service infrastructure.

This repository brings together the technical deliverables developed during the **Datheon Forward Deployed Engineering Internship**, organized into independent task directories with their own implementation, documentation, tests, and supporting resources.

## Project Overview

The four projects cover different layers of building practical AI systems, from preparing enterprise data and retrieving authorized information to orchestrating business workflows and operating an observable API service.

## Projects

### Task 1 — LegacyAI: Legacy Document Ingestion & Vector ETL Pipeline

**Focus:** Enterprise document processing, embeddings, vector databases, and semantic search.

LegacyAI transforms legacy documents into searchable vector representations. It supports PDF, CSV, and Markdown ingestion, text extraction, chunking, metadata preservation, embedding generation, persistent ChromaDB storage, and metadata-filtered semantic retrieval.

**Key technologies:** Python, PyMuPDF, Pandas, Pydantic, Sentence Transformers, ChromaDB, Pytest.

**Key engineering concepts:**
- Multi-format document ingestion.
- Modular extraction and chunking pipelines.
- Semantic embeddings and cosine-distance retrieval.
- Metadata preservation and filtering.
- Batch ingestion benchmarking and automated testing.

**Project links:** [Open Task 1 on GitHub](./Task_1_LegacyAI/) · [Read Task 1 documentation](./Task_1_LegacyAI/README.md)

---

### Task 2 — EnterpriseRAG: Secure Enterprise Retrieval-Augmented Generation

**Focus:** Access-controlled enterprise knowledge retrieval and grounded AI responses.

EnterpriseRAG combines semantic retrieval with role-based access control (RBAC), tenant-aware filtering, query rewriting, cross-encoder reranking, source citations, and answer validation. It is designed to restrict retrieved information according to the requesting user's access permissions before using that information to generate an answer.

**Key technologies:** Python, FastAPI, Streamlit, ChromaDB, Sentence Transformers, Gemini, Pytest.

**Key engineering concepts:**
- Retrieval-augmented generation (RAG).
- Tenant isolation and access-aware retrieval.
- Role and clearance-based filtering.
- Query rewriting and cross-encoder reranking.
- Source attribution and evidence-grounded responses.
- API and interactive frontend integration.

**Project links:** [Open Task 2 on GitHub](./Task_2_EnterpriseRAG/) · [Read Task 2 documentation](./Task_2_EnterpriseRAG/README.md)

---

### Task 3 — MultiAI: Autonomous Enterprise ERP/CRM Field Agent

**Focus:** Natural-language business workflows and controlled tool orchestration.

MultiAI is designed to translate natural-language requests into structured enterprise ERP and CRM operations. Its intended workflow combines registered business tools, validated action proposals, permission checks, human approval for operations that modify records, idempotency, bounded retries, and audit

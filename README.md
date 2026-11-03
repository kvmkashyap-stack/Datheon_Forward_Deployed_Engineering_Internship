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

MultiAI is designed to translate natural-language requests into structured enterprise ERP and CRM operations. Its intended workflow combines registered business tools, validated action proposals, permission checks, human approval for operations that modify records, idempotency, bounded retries, and audit logging.

The initial design uses simulated ERP and CRM records rather than live enterprise systems. Refer to the project documentation and implementation checklist for the actual implementation status of individual capabilities.

**Planned technologies:** Python, LangChain, LangGraph, Gemini, FastAPI, Streamlit, Pydantic, Pytest.

**Key engineering concepts:**
- Agentic workflows and tool orchestration.
- Structured action validation.
- Controlled execution of business operations.
- Human-in-the-loop approval.
- Idempotency and failure handling.
- Auditability and deterministic backend safeguards.

**Project links:** [Open Task 3 on GitHub](./Task_3_MultiAI/) · [Read Task 3 documentation](./Task_3_MultiAI/README.md)

---

### Task 4 — ProductionAIService: Containerized AI Microservice

**Focus:** API engineering, observability, container hardening, and performance benchmarking.

ProductionAIService provides a FastAPI-based service with generation and health endpoints, Prometheus instrumentation, environment-based configuration, security-oriented Docker settings, automated tests, and a concurrent HTTP benchmark.

The current implementation uses a mock AI provider. Docker configuration and Compose validation are available, while container runtime verification and deployment to a client VPC remain outstanding.

**Key technologies:** Python 3.12, FastAPI, Uvicorn, Pydantic Settings, Prometheus Client, Docker, Docker Compose, Pytest, HTTPX.

**Key engineering concepts:**
- REST API design and request validation.
- Health and readiness checks.
- Request latency, error, and token-count metrics.
- Environment-based secrets configuration.
- Non-root containers and restricted runtime privileges.
- p50, p95, p99 latency, throughput, and failure-rate benchmarking.

**Recorded local mock-provider benchmark:** 100 requests, 10 concurrent requests, 0% observed failures, and 154.47 requests/second in the recorded run. These are local mock-service results, not real-model or production VPC performance measurements.

**Project links:** [Open Task 4 on GitHub](./Task_4_ProductionAIService/) · [Read Task 4 documentation](./Task_4_ProductionAIService/README.md)

---

## Repository Structure

```text
Datheon_Forward_Deployed_Engineering_Internship/
│
├── Task_1_LegacyAI/
│   └── README.md
│
├── Task_2_EnterpriseRAG/
│   └── README.md
│
├── Task_3_MultiAI/
│   └── README.md
│
├── Task_4_ProductionAIService/
│   └── README.md
│
└── README.md
```

Each task directory contains its own project documentation and associated implementation resources.

## Overall Architecture and Learning Progression

```text
Enterprise Data Engineering
          |
          v
Task 1 — LegacyAI
Document ingestion, embeddings, vector storage
          |
          v
Task 2 — EnterpriseRAG
Authorized retrieval, reranking, grounded answers
          |
          v
Task 3 — MultiAI
Agent workflows, tool orchestration, approval controls
          |
          v
Task 4 — ProductionAIService
API operations, metrics, container configuration
          |
          v
Enterprise AI Engineering Foundations
```

The diagram represents the conceptual progression across the projects. The four tasks are separate deliverables rather than a single integrated application.

## Cross-Project Engineering Themes

Across the repository, the projects explore several complementary areas of AI engineering:

- **Data pipelines:** Converting heterogeneous enterprise data into structured, searchable representations.
- **Retrieval systems:** Using semantic search and ranking to locate relevant information.
- **Security and access control:** Restricting information retrieval and controlling sensitive business operations.
- **Agentic systems:** Connecting language-model-driven workflows to explicitly registered tools and validation logic.
- **Backend engineering:** Designing modular Python services and HTTP APIs.
- **Observability:** Exposing metrics and measuring application behavior.
- **Testing and benchmarking:** Validating components and collecting measurable performance results.
- **Deployment foundations:** Defining configuration and container settings for repeatable execution.

## Getting Started

1. Open the task directory you want to explore using the links above.
2. Read that task's `README.md` for its architecture, dependencies, setup instructions, and current limitations.
3. Follow the task-specific installation instructions.
4. Run its documented tests and benchmarks where supported.
5. Review the implementation status before assuming a documented capability has been fully implemented or verified.

Dependencies and setup requirements differ between projects. Use each task's own instructions rather than assuming one shared Python environment works for all four.

## Repository

**GitHub:** [kvmkashyap-stack/Datheon_Forward_Deployed_Engineering_Internship](https://github.com/kvmkashyap-stack/Datheon_Forward_Deployed_Engineering_Internship)

Browse the repository to explore the individual implementations, technical documentation, tests, and benchmark artifacts.

---

*Maintained as a portfolio of engineering work completed as part of the Datheon Forward Deployed Engineering Internship. Implementation status, test results, and deployment claims should be evaluated against the documentation and verification evidence for each individual task.*

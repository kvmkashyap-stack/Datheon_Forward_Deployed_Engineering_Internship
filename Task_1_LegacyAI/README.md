# Task 1 — LegacyAI: Legacy Document Ingestion & Vector ETL Pipeline

## 1. Project Overview

LegacyAI is a document ingestion and vector ETL pipeline designed to transform legacy enterprise documents into searchable, metadata-rich vector representations.

The system ingests PDF, CSV, and Markdown files, extracts their contents, splits documents into overlapping chunks, generates semantic embeddings, and stores the resulting vectors in a persistent ChromaDB collection.

It preserves document metadata throughout the ingestion pipeline and supports semantic retrieval with metadata-based filtering. An ingestion benchmark measures how different batch sizes affect processing performance.

This project demonstrates practical skills in document processing, data engineering, semantic search, vector databases, metadata management, Python packaging, automated testing, and performance benchmarking.

## 2. Objectives

The main objectives of LegacyAI are to:

- Ingest multiple legacy document formats through a unified pipeline.
- Extract text and structured information from heterogeneous sources.
- Split extracted content into manageable, overlapping chunks.
- Preserve document provenance and business metadata.
- Generate semantic embeddings using Sentence Transformers.
- Store embeddings in a persistent vector database.
- Perform semantic similarity searches using cosine distance.
- Filter retrieved documents using metadata constraints.
- Benchmark ingestion performance across different batch sizes.
- Validate system behavior using automated tests.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| PDF extraction | PyMuPDF |
| CSV processing | Pandas |
| Markdown processing | Python |
| Data validation | Pydantic |
| Embedding model | Sentence Transformers |
| Embedding model identifier | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| Similarity metric | Cosine distance |
| Testing framework | Pytest |
| Packaging and build system | Hatchling |
| Command-line interface | Python CLI entry point |

## 4. Project Structure

```text
Task_1_LegacyAI/
│
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
│
├── data/
│   ├── raw/
│   │   ├── pdf/
│   │   ├── csv/
│   │   └── markdown/
│   │
│   └── processed/
│
├── src/
│   └── legacyai/
│       ├── __init__.py
│       ├── config.py
│       ├── models.py
│       ├── chunking.py
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── metadata.py
│       ├── ingestion.py
│       ├── retrieval.py
│       ├── cli.py
│       │
│       └── extractors/
│           ├── __init__.py
│           ├── pdf_extractor.py
│           ├── csv_extractor.py
│           └── markdown_extractor.py
│
├── benchmarks/
│   ├── __init__.py
│   └── benchmark_ingestion.py
│
└── tests/
    ├── conftest.py
    ├── test_extractors.py
    ├── test_chunking.py
    ├── test_embeddings.py
    ├── test_vector_store.py
    ├── test_ingestion.py
    ├── test_retrieval.py
    └── test_metadata.py
```

Note: `.venv/`, `.env`, local source documents, generated vector database files, Python caches, and benchmark output files are excluded from version control.

## 5. System Architecture

The system follows a modular ingestion and retrieval architecture.

```text
                  Legacy Documents
                         |
             +-----------+-----------+
             |           |           |
            PDF         CSV       Markdown
             |           |           |
             v           v           v
          PDF         CSV         Markdown
        Extractor   Extractor     Extractor
             |           |           |
             +-----------+-----------+
                         |
                         v
                Extracted Documents
                         |
                         v
                Metadata Validation
                         |
                         v
                 Text Chunking
                         |
                         v
                Embedding Generation
                         |
                         v
                Batch Vector Upsert
                         |
                         v
                  Persistent ChromaDB
                         |
                         v
                 Semantic Retrieval
                         |
                         v
                Metadata Filtering
                         |
                         v
                  Ranked Results
```

The architecture separates extraction, validation, chunking, embedding generation, storage, and retrieval into independent modules. This makes individual components easier to test, maintain, and extend.

## 6. Installation and Setup

### Prerequisites

- Python 3.11 or newer.
- Git.
- PowerShell or another compatible terminal.
- An internet connection for installing dependencies and downloading the embedding model on its first use.

### Step 1: Navigate to the project directory

From the internship repository root:

```powershell
cd .\Task_1_LegacyAI
```

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

### Step 3: Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the following command for the current terminal session if your execution policy permits it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### Step 4: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 5: Install the dependencies

Install the project and its development dependencies in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

This installs the project dependencies and makes the `legacyai` command available in the active environment.

Alternatively, install the declared requirements and the editable project separately:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

### Step 6: Verify the CLI

```powershell
legacyai --help
```

The command should display the available CLI commands and their usage information.

## 7. Preparing Input Documents

The ingestion pipeline supports three input formats:

- PDF documents.
- CSV files.
- Markdown files.

Create the input directories if they do not already exist:

```powershell
New-Item -ItemType Directory -Force -Path `
    ".\data\raw\pdf", `
    ".\data\raw\csv", `
    ".\data\raw\markdown", `
    ".\data\processed"
```

Place the documents you want to process in the appropriate subdirectories.

Example:

```text
data/
└── raw/
    ├── pdf/
    │   └── employee_handbook.pdf
    ├── csv/
    │   └── employee_records.csv
    └── markdown/
        └── leave_policy.md
```

These are illustrative filenames. Use your own documents or the sample documents created for local testing.

The input directory is intentionally excluded from Git to prevent accidentally committing private, sensitive, or large source documents.

## 8. Document Extraction

### PDF extraction

The PDF extractor uses PyMuPDF to open PDF documents and extract text from their pages.

The extracted text is passed to the common document-processing pipeline.

### CSV extraction

The CSV extractor uses Pandas to read CSV files. Each non-empty row is represented as structured, JSON-formatted content, making the row's fields available for downstream processing and semantic retrieval.

### Markdown extraction

The Markdown extractor processes document sections and preserves heading context so that chunks retain useful information about the section from which they originated.

All extractors produce documents compatible with the common ingestion pipeline.

## 9. Metadata Management

Metadata is essential when enterprise documents have different departments, access classifications, or dates.

LegacyAI uses Pydantic models to validate document metadata.

The supported metadata fields include:

- `department`: The department associated with a document.
- `access_tier`: The document's access classification.
- `document_date`: The associated document date.

Supported access tiers are:

- `public`
- `internal`
- `confidential`
- `restricted`

Metadata validation helps reject invalid classifications and ensures that document attributes remain consistent across extraction, chunking, storage, and retrieval.

The metadata module also converts metadata into a form supported by ChromaDB and constructs metadata filters.

**Security note:** Metadata filtering is a retrieval capability, not a complete authorization system. Production deployments must enforce access control independently and must not rely on a user-supplied filter as the sole security boundary.

## 10. Text Chunking

Large documents are divided into smaller, overlapping chunks before embedding generation.

The chunking module:

- Splits document text into manageable segments.
- Supports overlap between consecutive chunks.
- Prefers suitable text boundaries when possible.
- Preserves document metadata across chunks.

Chunking improves the granularity of semantic retrieval and helps return relevant passages instead of requiring every search result to represent an entire document.

Overlap helps retain context when relevant information spans a chunk boundary.

## 11. Embedding Generation

LegacyAI uses Sentence Transformers with the model:

`sentence-transformers/all-MiniLM-L6-v2`

The embedding module converts text chunks into numerical vectors representing their semantic content.

The vectors are normalized before storage.

Semantic embeddings allow the system to compare the meaning of a query with the meaning of stored document chunks, rather than relying exclusively on exact keyword matches.

The model may need to be downloaded the first time it is used. Subsequent runs can reuse the locally cached model, depending on the environment.

## 12. Vector Storage

ChromaDB is used as the persistent vector database.

The vector-store module:

- Initializes a persistent ChromaDB client.
- Configures the collection to use cosine distance.
- Stores document chunks and their embeddings.
- Preserves compatible metadata.
- Supports batch upserts.
- Allows stored vectors to be queried semantically.

The local database is stored in `chroma_db/` by default and is excluded from Git.

Persistent storage allows the database to be reused between local executions without rebuilding it every time.

## 13. Running the Ingestion Pipeline

After installing the project and preparing the input documents, run the following command from the `Task_1_LegacyAI` directory:

```powershell
legacyai ingest --path .\data\raw --department engineering --access-tier internal --document-date 2026-10-24
```

This command demonstrates ingestion with:

- Input path: `data/raw`
- Department: `engineering`
- Access tier: `internal`
- Document date: `2026-10-24`

Replace the example metadata values with the appropriate values for your documents.

The ingestion pipeline discovers supported files, extracts their contents, validates and preserves metadata, generates chunks, creates embeddings, and stores the resulting records in ChromaDB.

### Example ingestion output

A representative local sample run produced:

```json
{
  "files_processed": 3,
  "documents_extracted": 22,
  "chunks_created": 46,
  "chunks_stored": 46
}
```

These figures describe the sample dataset used during development. Actual results depend on the input files and their contents.

## 14. Semantic Search and Retrieval

Once documents have been ingested, search the stored chunks using a natural-language query.

Example:

```powershell
legacyai search --query "employee leave policy" --top-k 3
```

The search pipeline:

1. Accepts the user's query.
2. Generates a query embedding using the configured embedding model.
3. Searches the ChromaDB collection using vector similarity.
4. Returns the top matching chunks.
5. Includes relevant document metadata and distance information.

The `--top-k` argument controls the number of results requested.

Because ChromaDB uses cosine distance here, smaller distance values indicate greater similarity under this distance metric. The returned distances should not be interpreted as calibrated probabilities or confidence scores.

### Metadata-filtered search

A search can be restricted by department using the supported CLI option:

```powershell
legacyai search --query "employee leave policy" --top-k 3 --department engineering
```

A query using a department that does not match any stored records can be used to verify filtering behavior:

```powershell
legacyai search --query "employee leave policy" --top-k 3 --department nonexistent_department
```

For the development sample, the nonexistent-department query returned an empty result list.

Metadata filters help narrow search results to records matching the requested attributes.

## 15. Ingestion Performance Benchmarking

LegacyAI includes a benchmarking module for measuring ingestion performance across different batch sizes.

Run the benchmark from the project root:

```powershell
python -m benchmarks.benchmark_ingestion --path .\data\raw --batch-sizes 16 32 64 100
```

The benchmark measures processing performance for the selected batch sizes and reports elapsed time and throughput.

Separate persistent database paths are used for benchmark runs to avoid interference between benchmark iterations and Windows file-locking issues.

### Example benchmark results

One local run produced the following results:

| Batch size | Elapsed time (seconds) | Throughput (chunks/second) |
|---:|---:|---:|
| 16 | 3.3177 | 13.86 |
| 32 | 1.1349 | 40.53 |
| 64 | 0.9091 | 50.60 |
| 100 | 1.4012 | 32.83 |

The sample benchmark processed three files, extracted 22 documents, and created and stored 46 chunks.

In this particular run, batch size 64 achieved the highest throughput among the tested values.

These results are specific to the local environment and sample dataset. They are not a universal performance guarantee. Larger datasets, hardware differences, model loading, storage performance, and document characteristics can change the results.

Benchmark output files are excluded from version control.

## 16. Automated Testing

LegacyAI includes automated tests for the core pipeline components.

The test suite covers:

- PDF, CSV, and Markdown extraction.
- Text chunking.
- Metadata validation and conversion.
- Embedding generation.
- Vector-store behavior.
- Document ingestion.
- Semantic retrieval.

Run the tests from the project root:

```powershell
pytest -v
```

Alternatively:

```powershell
python -m pytest -v
```

During development, the suite reported:

```text
36 passed, 1 warning in 20.69s
```

That result was recorded before the PDF extractor was updated to use the modern `pymupdf` import.

The PDF import was subsequently updated, but the above test result should not be treated as confirmation of the post-change test run. Rerun the suite in the current environment to confirm the final result.

## 17. Configuration and Dependencies

### `requirements.txt`

Lists the primary dependencies required by the project.

### `pyproject.toml`

Defines the project metadata, Python requirement, package dependencies, build configuration, test configuration, and CLI entry point.

The package is installed using Hatchling as its build backend.

### `.gitignore`

Excludes local and generated files, including:

- Virtual environments.
- Python bytecode and test caches.
- Environment variable files.
- Local source data.
- PDF and CSV files.
- ChromaDB data.
- Generated benchmark results.
- IDE-specific files and operating-system artifacts.

Never commit credentials, private documents, or environment-specific secrets to a public repository.

## 18. Design Decisions

### Modular architecture

Separating extraction, chunking, metadata, embeddings, storage, and retrieval keeps the code organized and makes components independently testable.

### Normalized embeddings and cosine distance

Normalized embeddings and cosine distance provide a consistent basis for semantic similarity comparisons.

### Persistent vector storage

Persistent ChromaDB storage makes it possible to reuse ingested records across executions.

### Metadata preservation

Carrying metadata through the pipeline allows search results to retain useful context about their source and classification.

### Batch processing

Batch upserts reduce the overhead of issuing storage operations individually. Benchmarking helps evaluate the trade-offs between batch sizes.

### Automated tests

Automated tests help detect regressions in extraction, validation, chunking, storage, and retrieval as the implementation evolves.

## 19. Current Scope and Limitations

LegacyAI is an ingestion and semantic retrieval pipeline rather than a complete enterprise document-management platform.

The current implementation focuses on:

- PDF, CSV, and Markdown ingestion.
- Metadata-aware document processing.
- Embedding generation and persistent vector storage.
- Semantic retrieval and metadata filtering.
- Batch ingestion benchmarking.
- Automated testing.

The project does not, by itself, provide a complete authentication system, enterprise authorization enforcement, document-level permission management, a user interface, or a production deployment configuration.

Scanned PDFs that contain images rather than extractable text may require an OCR stage. Large-scale deployments may also require additional monitoring, incremental update strategies, robust error recovery, and workload-specific performance testing.

## 20. Future Improvements

Potential extensions include:

- OCR support for scanned PDFs.
- Incremental ingestion and document version tracking.
- Duplicate detection and content hashing.
- Improved chunking strategies for different document types.
- More extensive benchmark datasets and repeatable benchmark runs.
- Stronger document-level access-control integration.
- Structured logging and ingestion error reporting.
- Monitoring and operational metrics.
- Additional retrieval evaluation metrics.
- Containerized deployment for reproducible environments.

These are potential improvements, not claims about functionality already implemented.

## 21. Running the Complete Workflow

The following commands summarize the standard local workflow.

### Install and activate

```powershell
cd .\Task_1_LegacyAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Prepare data

Place PDF, CSV, and Markdown documents under `data/raw/`.

### Ingest documents

```powershell
legacyai ingest --path .\data\raw --department engineering --access-tier internal --document-date 2026-10-24
```

### Search documents

```powershell
legacyai search --query "employee leave policy" --top-k 3
```

### Test the implementation

```powershell
pytest -v
```

### Benchmark ingestion

```powershell
python -m benchmarks.benchmark_ingestion --path .\data\raw --batch-sizes 16 32 64 100
```

Run these commands in the same project environment so that the CLI, dependencies, embedding model, and local vector database are available.

## 22. Conclusion

LegacyAI demonstrates an end-to-end document ingestion and semantic retrieval workflow for heterogeneous legacy data sources.

By combining modular extraction, metadata validation, overlapping text chunking, normalized semantic embeddings, persistent vector storage, metadata-aware retrieval, and batch-size benchmarking, the project establishes a foundation for building more advanced enterprise knowledge retrieval systems.

The implementation emphasizes modularity, reproducibility, data provenance, automated testing, and measurable performance.

---

**Project:** Task 1 — LegacyAI  
**Internship:** Forward Deployed Engineering Internship  
**Repository:** Datheon Forward Deployed Engineering Internship  
**Primary language:** Python  
**Core focus:** Document ingestion, vector ETL, semantic search, metadata filtering, and performance benchmarking

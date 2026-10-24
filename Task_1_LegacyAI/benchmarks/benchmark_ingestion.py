
import argparse
import json
import time
from datetime import date, datetime
from pathlib import Path

from legacyai.config import RAW_DATA_DIR
from legacyai.ingestion import ingest_directory
from legacyai.vector_store import VectorStore


def run_benchmark(
    source_directory: Path,
    batch_sizes: list[int],
    department: str,
    access_tier: str,
    document_date: date,
) -> list[dict[str, float | int]]:
    """Measure ingestion duration and throughput for each batch size."""

    if not source_directory.is_dir():
        raise NotADirectoryError(
            f"Source directory not found: {source_directory}"
        )

    results_directory = Path(__file__).resolve().parent / "results"
    results_directory.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    for batch_size in batch_sizes:
        database_path = (
            results_directory
            / f"chroma_{run_id}_batch_{batch_size}"
        )

        store = VectorStore(
            persist_directory=database_path,
            collection_name="benchmark_documents",
        )

        start_time = time.perf_counter()

        ingestion_result = ingest_directory(
            directory=source_directory,
            department=department,
            access_tier=access_tier,
            document_date=document_date,
            vector_store=store,
            batch_size=batch_size,
        )

        elapsed_seconds = time.perf_counter() - start_time
        chunks_stored = ingestion_result["chunks_stored"]

        chunks_per_second = (
            chunks_stored / elapsed_seconds
            if elapsed_seconds > 0
            else 0.0
        )

        results.append(
            {
                "batch_size": batch_size,
                "elapsed_seconds": round(elapsed_seconds, 4),
                "files_processed": ingestion_result["files_processed"],
                "documents_extracted": ingestion_result[
                    "documents_extracted"
                ],
                "chunks_created": ingestion_result["chunks_created"],
                "chunks_stored": chunks_stored,
                "chunks_per_second": round(chunks_per_second, 2),
            }
        )

        print(
            f"Completed batch size {batch_size}: "
            f"{chunks_stored} chunks in {elapsed_seconds:.2f}s"
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark the LegacyAI vector ingestion pipeline"
    )

    parser.add_argument(
        "--path",
        type=Path,
        default=RAW_DATA_DIR,
        help="Directory containing PDF, CSV, and Markdown files",
    )
    parser.add_argument(
        "--batch-sizes",
        nargs="+",
        type=int,
        default=[16, 32, 64, 100],
    )
    parser.add_argument("--department", default="engineering")
    parser.add_argument(
        "--access-tier",
        choices=["public", "internal", "confidential", "restricted"],
        default="internal",
    )
    parser.add_argument(
        "--document-date",
        type=date.fromisoformat,
        default=date.today(),
    )

    args = parser.parse_args()

    if any(size <= 0 for size in args.batch_sizes):
        parser.error("All batch sizes must be positive integers")

    results = run_benchmark(
        source_directory=args.path,
        batch_sizes=args.batch_sizes,
        department=args.department,
        access_tier=args.access_tier,
        document_date=args.document_date,
    )

    print("\nBenchmark results:")
    print(json.dumps(results, indent=2))

    fastest = min(results, key=lambda item: item["elapsed_seconds"])
    print(
        "\nFastest measured configuration: "
        f"batch_size={fastest['batch_size']}, "
        f"time={fastest['elapsed_seconds']} seconds"
    )


if __name__ == "__main__":
    main()

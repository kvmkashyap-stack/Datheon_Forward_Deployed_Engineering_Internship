
import argparse
import json
from datetime import date

from legacyai.config import RAW_DATA_DIR
from legacyai.ingestion import ingest_directory, ingest_file
from legacyai.models import AccessTier
from legacyai.retrieval import search_documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LegacyAI document ingestion and search pipeline"
    )

    commands = parser.add_subparsers(dest="command", required=True)

    ingest = commands.add_parser("ingest", help="Ingest client documents")
    ingest.add_argument("--path", default=str(RAW_DATA_DIR))
    ingest.add_argument("--department", required=True)
    ingest.add_argument(
        "--access-tier",
        choices=["public", "internal", "confidential", "restricted"],
        required=True,
    )
    ingest.add_argument(
        "--document-date",
        type=date.fromisoformat,
        required=True,
    )
    ingest.add_argument("--batch-size", type=int, default=100)

    search = commands.add_parser("search", help="Search ingested documents")
    search.add_argument("--query", required=True)
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--department")
    search.add_argument(
        "--access-tier",
        choices=["public", "internal", "confidential", "restricted"],
    )
    search.add_argument("--document-date", type=date.fromisoformat)

    args = parser.parse_args()

    if args.command == "ingest":
        from pathlib import Path

        source = Path(args.path)

        common = {
            "department": args.department,
            "access_tier": args.access_tier,
            "document_date": args.document_date,
            "batch_size": args.batch_size,
        }

        if source.is_file():
            result = ingest_file(source, **common)
        else:
            result = ingest_directory(source, **common)

        print(json.dumps(result, indent=2))

    elif args.command == "search":
        results = search_documents(
            query=args.query,
            top_k=args.top_k,
            department=args.department,
            access_tier=args.access_tier,
            document_date=args.document_date,
        )

        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()

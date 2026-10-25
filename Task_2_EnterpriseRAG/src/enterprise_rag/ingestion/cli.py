
import argparse
import json
import sys
from pathlib import Path

from enterprise_rag.ingestion.service import ingest_pdf
from enterprise_rag.models import ClearanceLevel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest a PDF into the EnterpriseRAG vector database."
    )

    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to the PDF file.",
    )
    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Tenant that owns the document.",
    )
    parser.add_argument(
        "--classification",
        required=True,
        choices=[level.name.lower() for level in ClearanceLevel],
        help="Document classification level.",
    )
    parser.add_argument(
        "--source-id",
        default=None,
        help="Optional stable source identifier. Defaults to the PDF filename stem.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser()

    try:
        classification = ClearanceLevel[args.classification.upper()]

        result = ingest_pdf(
            file_path=pdf_path,
            tenant_id=args.tenant_id,
            classification=classification,
            source_id=args.source_id,
        )

        print(json.dumps(result, indent=2))
        return 0

    except (OSError, ValueError) as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

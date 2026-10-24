import json
from pathlib import Path
import pandas as pd
from legacyai.models import DocumentMetadata, ExtractedDocument


def extract_csv(
    file_path: str | Path,
    metadata: DocumentMetadata,
) -> list[ExtractedDocument]:
    """Convert each non-empty CSV row into a normalized document."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file, got: {path.name}")

    dataframe = pd.read_csv(path, dtype=str, keep_default_na=False)

    if dataframe.empty:
        return []

    documents: list[ExtractedDocument] = []

    for row_number, row in enumerate(
        dataframe.to_dict(orient="records"),
        start=2,
    ):
        cleaned_row = {
            str(key).strip(): str(value).strip()
            for key, value in row.items()
        }

        cleaned_row = {
            key: value
            for key, value in cleaned_row.items()
            if key and value
        }

        if not cleaned_row:
            continue

        content = json.dumps(
            cleaned_row,
            ensure_ascii=False,
            sort_keys=True,
        )

        documents.append(
            ExtractedDocument(
                document_id=f"{path.stem}-row-{row_number}",
                source_path=str(path.resolve()),
                source_type="csv",
                content=content,
                metadata=metadata,
            )
        )

    return documents

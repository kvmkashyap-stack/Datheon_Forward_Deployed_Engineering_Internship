import re
from pathlib import Path
from legacyai.models import DocumentMetadata, ExtractedDocument


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def extract_markdown(
    file_path: str | Path,
    metadata: DocumentMetadata,
) -> list[ExtractedDocument]:
    """Extract Markdown sections with their heading context."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {path}")

    if path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError(f"Expected a Markdown file, got: {path.name}")

    text = path.read_text(encoding="utf-8-sig").strip()

    if not text:
        return []

    sections: list[tuple[str, list[str]]] = []
    heading_stack: list[str] = []
    current_lines: list[str] = []
    section_number = 0

    for line in text.splitlines():
        match = HEADING_PATTERN.match(line)

        if match:
            if any(item.strip() for item in current_lines):
                sections.append(
                    (" > ".join(heading_stack), current_lines)
                )

            level = len(match.group(1))
            heading = match.group(2).strip()

            heading_stack = heading_stack[: level - 1]
            heading_stack.append(heading)
            current_lines = []
            section_number += 1
        else:
            current_lines.append(line)

    if any(item.strip() for item in current_lines):
        sections.append((" > ".join(heading_stack), current_lines))

    if not sections:
        sections = [("", text.splitlines())]

    documents: list[ExtractedDocument] = []

    for index, (heading, lines) in enumerate(sections, start=1):
        body = "\n".join(lines).strip()

        if not body:
            continue

        content = f"Section: {heading}\n\n{body}" if heading else body

        documents.append(
            ExtractedDocument(
                document_id=f"{path.stem}-section-{index}",
                source_path=str(path.resolve()),
                source_type="markdown",
                content=content,
                metadata=metadata,
            )
        )

    return documents

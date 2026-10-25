import re
from langchain_core.documents import Document

CITATION_PATTERN = re.compile(
    r"\[Source:\s*(?P<source>[^,\]]+),\s*Page:\s*(?P<page>\d+)\]",
    re.IGNORECASE,
)


def available_citations(documents: list[Document]) -> set[tuple[str, int]]:
    """Build the set of source and page pairs present in retrieved evidence."""

    citations: set[tuple[str, int]] = set()

    for document in documents:
        source = document.metadata.get("source_name")
        page = document.metadata.get("page_number")

        if isinstance(source, str) and isinstance(page, int) and page >= 1:
            citations.add((source.strip(), page))

    return citations


def validate_citations(
    answer: str,
    documents: list[Document],
) -> bool:
    """Check that every emitted citation points to a retrieved source page."""

    matches = list(CITATION_PATTERN.finditer(answer))

    if not matches:
        return False

    available = available_citations(documents)

    for match in matches:
        source = match.group("source").strip()
        page = int(match.group("page"))

        if (source, page) not in available:
            return False

    return True

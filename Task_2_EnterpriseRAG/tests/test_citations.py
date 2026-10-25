
from langchain_core.documents import Document

from enterprise_rag.generation.citations import (
    available_citations,
    validate_citations,
)


def make_evidence(
    source: str = "employee_handbook.pdf",
    page: int = 3,
) -> Document:
    return Document(
        page_content="Employees receive annual leave.",
        metadata={
            "source_name": source,
            "page_number": page,
            "tenant_id": "tenant-alpha",
            "classification_level": 0,
        },
    )


def test_valid_source_and_page_citation() -> None:
    evidence = [make_evidence()]

    answer = (
        "Employees receive annual leave. "
        "[Source: employee_handbook.pdf, Page: 3]"
    )

    assert validate_citations(answer, evidence)


def test_fabricated_page_number_is_rejected() -> None:
    evidence = [make_evidence(page=3)]

    answer = "Annual leave is available. [Source: employee_handbook.pdf, Page: 99]"

    assert not validate_citations(answer, evidence)


def test_unknown_source_is_rejected() -> None:
    evidence = [make_evidence()]

    answer = "Policy applies. [Source: confidential.pdf, Page: 3]"

    assert not validate_citations(answer, evidence)


def test_missing_citation_is_rejected() -> None:
    evidence = [make_evidence()]

    assert not validate_citations(
        "Employees receive annual leave.",
        evidence,
    )


def test_available_citations_returns_source_page_pairs() -> None:
    evidence = [
        make_evidence(page=1),
        make_evidence(page=3),
        make_evidence(source="security_policy.pdf", page=2),
    ]

    assert available_citations(evidence) == {
        ("employee_handbook.pdf", 1),
        ("employee_handbook.pdf", 3),
        ("security_policy.pdf", 2),
    }

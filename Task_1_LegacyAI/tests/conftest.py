from datetime import date
import pytest
from legacyai.models import DocumentMetadata


@pytest.fixture
def sample_metadata() -> DocumentMetadata:
    return DocumentMetadata(
        department="HR",
        access_tier="internal",
        document_date=date(2026, 10, 24),
    )


@pytest.fixture
def sample_markdown(tmp_path):
    path = tmp_path / "employee_policy.md"
    path.write_text(
        "# Leave Policy\n\nEmployees receive annual leave.\n\n"
        "## Eligibility\n\nFull-time employees are eligible.\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "employees.csv"
    path.write_text(
        "name,department\n"
        "Alice,Engineering\n"
        "Bob,HR\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_pdf(tmp_path):
    import fitz

    path = tmp_path / "policy.pdf"

    with fitz.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "Company leave policy.")
        pdf.save(path)

    return path

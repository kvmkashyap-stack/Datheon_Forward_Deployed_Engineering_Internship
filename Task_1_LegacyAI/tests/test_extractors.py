from legacyai.extractors.csv_extractor import extract_csv
from legacyai.extractors.markdown_extractor import extract_markdown
from legacyai.extractors.pdf_extractor import extract_pdf


def test_pdf_extraction(sample_pdf, sample_metadata):
    documents = extract_pdf(sample_pdf, sample_metadata)

    assert len(documents) == 1
    assert documents[0].source_type == "pdf"
    assert "Company leave policy" in documents[0].content
    assert documents[0].document_id == "policy-page-1"


def test_csv_extraction(sample_csv, sample_metadata):
    documents = extract_csv(sample_csv, sample_metadata)

    assert len(documents) == 2
    assert documents[0].source_type == "csv"
    assert "Alice" in documents[0].content
    assert documents[0].document_id == "employees-row-2"


def test_markdown_extraction(sample_markdown, sample_metadata):
    documents = extract_markdown(sample_markdown, sample_metadata)

    assert len(documents) == 2
    assert documents[0].source_type == "markdown"
    assert "Leave Policy" in documents[0].content
    assert "Eligibility" in documents[1].content


def test_missing_pdf_raises_error(tmp_path, sample_metadata):
    missing_path = tmp_path / "missing.pdf"

    try:
        extract_pdf(missing_path, sample_metadata)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")

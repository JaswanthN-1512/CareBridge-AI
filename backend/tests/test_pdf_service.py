"""Tests for PDF extraction, validation, and text normalization service."""

import pytest
import fitz  # PyMuPDF
from app.services.pdf_service import PDFService, PDFServiceError
from app.utils.pdf_utils import validate_pdf_bytes
from app.utils.text_utils import clean_text, is_empty_or_whitespace


def create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Helper to construct an in-memory valid PDF byte buffer using PyMuPDF."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        if text.strip():
            page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_text_cleaning_and_whitespace():
    """Verify clean_text removes excessive tabs, spaces, and preserves paragraphs."""
    raw = "   Patient   Name:    John   Doe  \r\n\r\n\n\nResult:   Normal   "
    cleaned = clean_text(raw)
    assert cleaned == "Patient Name: John Doe\n\nResult: Normal"

    assert is_empty_or_whitespace("   \n\t  ") is True
    assert is_empty_or_whitespace("HbA1c 5.4%") is False


def test_pdf_validation_failures():
    """Verify validate_pdf_bytes detects empty, non-pdf, and oversized buffers."""
    is_valid, msg = validate_pdf_bytes(b"")
    assert is_valid is False
    assert "empty" in msg.lower()

    is_valid, msg = validate_pdf_bytes(b"NOT A REAL PDF FILE")
    assert is_valid is False
    assert "header signature" in msg.lower()

    is_valid, msg = validate_pdf_bytes(b"%PDF-" + b"0" * 200, max_size_mb=0)
    assert is_valid is False
    assert "exceeds maximum allowed limit" in msg.lower()


def test_pdf_extraction_multi_page():
    """Verify PDFService extracts text, pages, word counts, and page markers accurately."""
    service = PDFService()
    pages_content = [
        "Metabolic Health Clinic\nDate: 2026-10-15\nFasting Blood Glucose: 95 mg/dL",
        "Clinical Plan:\n1. Repeat lipid profile in 6 months.\n2. Maintain current physical activity.",
    ]
    pdf_bytes = create_in_memory_pdf(pages_content)

    doc_data = service.extract_document(pdf_bytes, filename="lab_test.pdf")

    assert doc_data["filename"] == "lab_test.pdf"
    assert doc_data["total_pages"] == 2
    assert doc_data["non_empty_pages"] == 2
    assert len(doc_data["pages"]) == 2

    # Check page 1
    p1 = doc_data["pages"][0]
    assert p1["page_number"] == 1
    assert "Fasting Blood Glucose: 95 mg/dL" in p1["text"]
    assert p1["is_empty"] is False
    assert p1["word_count"] > 0

    # Check page 2
    p2 = doc_data["pages"][1]
    assert p2["page_number"] == 2
    assert "Repeat lipid profile in 6 months" in p2["text"]
    assert p2["is_empty"] is False

    # Check full_text structure
    assert "--- [Page 1] ---" in doc_data["full_text"]
    assert "--- [Page 2] ---" in doc_data["full_text"]


def test_pdf_extraction_with_empty_page():
    """Verify empty pages within a document are cleanly flagged without breaking extraction."""
    service = PDFService()
    pages_content = [
        "Cover page with clinical metadata",
        "",  # blank page
        "Discharge medications: Metformin 500mg BID",
    ]
    pdf_bytes = create_in_memory_pdf(pages_content)

    doc_data = service.extract_document(pdf_bytes, filename="empty_page_test.pdf")

    assert doc_data["total_pages"] == 3
    assert doc_data["non_empty_pages"] == 2
    assert doc_data["pages"][1]["is_empty"] is True
    assert doc_data["pages"][1]["char_count"] == 0


def test_pdf_extraction_completely_blank_raises():
    """Verify completely blank PDF triggers a clear PDFServiceError."""
    service = PDFService()
    pdf_bytes = create_in_memory_pdf(["", "   "])

    with pytest.raises(PDFServiceError) as exc_info:
        service.extract_document(pdf_bytes, filename="blank.pdf")
    assert "no readable text" in str(exc_info.value).lower()

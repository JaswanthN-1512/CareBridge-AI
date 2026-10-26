"""Validation and security inspection utilities for incoming PDF files."""

from typing import Tuple
import fitz  # PyMuPDF


def validate_pdf_bytes(file_bytes: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
    """Validate that the uploaded byte buffer is a valid, readable, uncorrupted PDF.
    
    Performs:
    1. Size limit enforcement
    2. Magic byte header inspection (%PDF-)
    3. Structural parsing test using PyMuPDF
    4. Encryption check
    """
    if not file_bytes:
        return False, "Uploaded file is empty (0 bytes)."

    max_bytes = max_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return (
            False,
            f"File size exceeds maximum allowed limit of {max_size_mb} MB ({len(file_bytes)} bytes provided).",
        )

    # Magic byte verification: Valid PDFs must start with %PDF-
    if not file_bytes.startswith(b"%PDF-"):
        return False, "File is missing the standard PDF header signature (%PDF-). It may be corrupt or misnamed."

    # Structural verification with PyMuPDF
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        return False, f"Failed to parse PDF structure: {str(exc)}"

    try:
        if doc.is_encrypted:
            doc.close()
            return False, "This document is password-protected or encrypted. Please provide an unencrypted PDF."

        if doc.page_count == 0:
            doc.close()
            return False, "The PDF contains 0 pages."

        doc.close()
        return True, "Valid PDF."
    except Exception as exc:
        try:
            doc.close()
        except Exception:
            pass
        return False, f"Error validating PDF document: {str(exc)}"

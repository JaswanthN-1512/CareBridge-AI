"""PDF extraction and text preparation service using PyMuPDF (fitz)."""

import logging
from typing import Dict, Any, List
import fitz  # PyMuPDF

from app.utils.pdf_utils import validate_pdf_bytes
from app.utils.text_utils import clean_text, is_empty_or_whitespace

logger = logging.getLogger("carebridge.pdf_service")


class PDFServiceError(Exception):
    """Custom exception raised during PDF parsing failures."""
    pass


class PDFService:
    """High-performance document extraction service preserving page numbers and formatting."""

    def __init__(self, max_size_mb: int = 10):
        self.max_size_mb = max_size_mb

    def extract_document(self, file_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """Validate, extract, clean, and index all pages from a raw PDF byte stream.
        
        Returns:
            Dict containing:
            - filename: str
            - total_pages: int
            - non_empty_pages: int
            - pages: List[Dict[str, Any]] (each with page_number, text, char_count, is_empty)
            - full_text: str (concatenated with page boundary headers)
            - metadata: Dict[str, Any] (PDF author, creator, creationDate, etc.)
        """
        # Step 1: Pre-flight validation
        is_valid, validation_msg = validate_pdf_bytes(file_bytes, self.max_size_mb)
        if not is_valid:
            logger.error(f"Validation failed for {filename}: {validation_msg}")
            raise PDFServiceError(validation_msg)

        logger.info(f"Extracting text from {filename} ({len(file_bytes)} bytes)...")

        # Step 2: Open document stream
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            logger.error(f"Failed to open PDF stream for {filename}: {str(exc)}")
            raise PDFServiceError(f"Corrupt or unreadable PDF file: {str(exc)}")

        pages: List[Dict[str, Any]] = []
        full_text_fragments: List[str] = []
        total_chars = 0
        total_words = 0
        non_empty_count = 0

        try:
            total_pages = doc.page_count
            for pno in range(total_pages):
                page = doc.load_page(pno)
                page_number = pno + 1  # 1-indexed for patient clarity

                # Extract text preserving layout spacing
                raw_page_text = page.get_text("text")
                cleaned_page_text = clean_text(raw_page_text)
                is_empty = is_empty_or_whitespace(cleaned_page_text)

                char_count = len(cleaned_page_text)
                word_count = len(cleaned_page_text.split()) if not is_empty else 0

                if not is_empty:
                    non_empty_count += 1
                    total_chars += char_count
                    total_words += word_count
                    full_text_fragments.append(f"--- [Page {page_number}] ---\n{cleaned_page_text}")
                else:
                    full_text_fragments.append(f"--- [Page {page_number}] ---\n[Empty Page or Scanned Image without text]")

                pages.append({
                    "page_number": page_number,
                    "text": cleaned_page_text,
                    "char_count": char_count,
                    "word_count": word_count,
                    "is_empty": is_empty,
                })

            raw_meta = doc.metadata or {}
            metadata = {
                "title": raw_meta.get("title", ""),
                "author": raw_meta.get("author", ""),
                "creator": raw_meta.get("creator", ""),
                "creation_date": raw_meta.get("creationDate", ""),
            }

            full_text = "\n\n".join(full_text_fragments)

            logger.info(
                f"Successfully extracted {filename}: {total_pages} pages ({non_empty_count} non-empty), "
                f"{total_words} words, {total_chars} characters."
            )

            if non_empty_count == 0:
                raise PDFServiceError(
                    "The uploaded document contains no readable text. If this is a photographic scan or fax, "
                    "please provide a text-readable PDF."
                )

            return {
                "filename": filename,
                "total_pages": total_pages,
                "non_empty_pages": non_empty_count,
                "pages": pages,
                "metadata": metadata,
                "full_text": full_text,
                "total_words": total_words,
                "total_chars": total_chars,
            }

        finally:
            doc.close()

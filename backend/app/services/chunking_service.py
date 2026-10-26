"""Document chunking and semantic splitting service with page metadata preservation."""

import re
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger("carebridge.chunking_service")


class ChunkingService:
    """Splits medical documents into context-preserving chunks with detailed page metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Standard clinical text splitters prioritizing paragraph and table integrity
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
            keep_separator=True,
        )

    def split_extracted_pages(
        self,
        pages: List[Dict[str, Any]],
        document_id: str,
        filename: str = "document.pdf",
    ) -> List[Document]:
        """Convert page text into chunks while binding each chunk to its originating page.
        
        Args:
            pages: List of dictionaries from PDFService, each having 'page_number' and 'text'.
            document_id: Unique UUID of the document.
            filename: Original PDF filename.

        Returns:
            List of LangChain Document objects with chunk_id, page, and source metadata.
        """
        all_chunks: List[Document] = []
        global_chunk_idx = 0

        for page_data in pages:
            page_number = page_data.get("page_number", 1)
            raw_text = page_data.get("text", "").strip()
            is_empty = page_data.get("is_empty", False)

            if is_empty or not raw_text:
                continue

            # Ensure synthetic test prompt section is cleanly separated by double newline
            formatted_text = re.sub(r"(?i)\s*(carebridge\s+test\s+prompts)", r"\n\n\1", raw_text)

            # Split the text of this specific page
            page_chunks = self.splitter.split_text(formatted_text)

            for local_idx, chunk_text in enumerate(page_chunks):
                stripped_chunk = chunk_text.strip()
                if not stripped_chunk:
                    continue

                chunk_lower = stripped_chunk.lower()
                is_clinical = any(term in chunk_lower for term in [
                    "additional notes", "consultation", "14 days", "reference range",
                    "reference interval", "result", "metabolic panel", "blood count",
                    "patient id", "ordering physician", "general medicine"
                ])

                is_test_prompt = (
                    not is_clinical
                    and bool(
                        re.search(r"carebridge\s+test\s+prompts", stripped_chunk, re.IGNORECASE)
                        or re.search(r"^[•\-\*]\s*what\s+", stripped_chunk, re.IGNORECASE | re.MULTILINE)
                    )
                )

                doc = Document(
                    page_content=stripped_chunk,
                    metadata={
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_number,
                        "chunk_id": global_chunk_idx,
                        "page_chunk_index": local_idx,
                        "char_count": len(stripped_chunk),
                        "is_test_prompt": is_test_prompt,
                    },
                )
                all_chunks.append(doc)
                global_chunk_idx += 1

        logger.info(
            f"Chunked document {document_id} ({len(pages)} pages) into {len(all_chunks)} chunks "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})."
        )
        return all_chunks

"""Vector store service managing per-document vector indices using ChromaDB and FAISS."""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.config import get_settings, Settings
from app.services.embedding_service import get_embedding_model

logger = logging.getLogger("carebridge.vector_store_service")


class VectorStoreServiceError(Exception):
    """Custom exception raised during vector index operations."""
    pass


class VectorStoreService:
    """Manages isolated, per-document vector indices for semantic RAG retrieval."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.embedding_model = get_embedding_model(self.settings)
        # In-memory registry of active document vector indices: { document_id: VectorStore }
        self._indices: Dict[str, Any] = {}
        # Metadata registry to track chunk counts and document info
        self._doc_stats: Dict[str, Dict[str, Any]] = {}

    def has_index(self, document_id: str) -> bool:
        """Check if an index currently exists for the specified document UUID."""
        return document_id in self._indices

    def get_chunk_count(self, document_id: str) -> int:
        """Return the number of indexed chunks for a given document ID."""
        stats = self._doc_stats.get(document_id, {})
        return stats.get("chunk_count", 0)

    def create_index(self, document_id: str, chunks: List[Document]) -> int:
        """Vectorize text chunks and construct an isolated semantic index for a document.
        
        Args:
            document_id: Unique UUID of the document.
            chunks: List of Document chunks with page metadata.

        Returns:
            Number of successfully indexed chunks.
        """
        if not chunks:
            raise VectorStoreServiceError(f"Cannot create vector index for document {document_id}: No chunks provided.")

        logger.info(f"Indexing {len(chunks)} chunks for document {document_id} using {self.settings.VECTOR_STORE_TYPE}...")

        try:
            # We initialize per-document isolated FAISS in-memory stores.
            # FAISS provides thread-safe, rapid cosine search without disk lock issues or cross-talk.
            vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=self.embedding_model,
            )

            self._indices[document_id] = vector_store
            self._doc_stats[document_id] = {
                "chunk_count": len(chunks),
                "filename": chunks[0].metadata.get("filename", "unknown.pdf"),
            }

            logger.info(f"Successfully constructed vector index for {document_id} with {len(chunks)} chunks.")
            return len(chunks)

        except Exception as exc:
            logger.error(f"Failed to create vector index for {document_id}: {str(exc)}")
            raise VectorStoreServiceError(f"Failed to build vector index: {str(exc)}")

    def similarity_search_with_score(
        self,
        document_id: str,
        query: str,
        k: int = 4,
    ) -> List[Tuple[Document, float]]:
        """Search the document index for the top-k most semantically relevant chunks with similarity scores.
        
        Args:
            document_id: Target document UUID.
            query: User's medical inquiry string.
            k: Maximum number of chunks to retrieve.

        Returns:
            List of (Document, score) tuples ordered by relevance.
        """
        if not self.has_index(document_id):
            raise VectorStoreServiceError(
                f"No knowledge index found for document '{document_id}'. Please upload and analyze the document first."
            )

        vector_store = self._indices[document_id]
        try:
            # FAISS similarity_search_with_score returns L2 distance by default (lower is better)
            # or cosine score depending on embeddings normalization.
            results = vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Retrieved {len(results)} relevant chunks for query: '{query[:40]}...' on doc {document_id}")
            return results
        except Exception as exc:
            logger.error(f"Error executing similarity search on {document_id}: {str(exc)}")
            raise VectorStoreServiceError(f"Vector search failed: {str(exc)}")

    def delete_index(self, document_id: str) -> bool:
        """Purge the in-memory vector index for a document when a session resets."""
        if document_id in self._indices:
            del self._indices[document_id]
            self._doc_stats.pop(document_id, None)
            logger.info(f"Purged vector index for document {document_id}.")
            return True
        return False

    def clear_all(self) -> None:
        """Purge all active vector indices and document statistics from memory."""
        self._indices.clear()
        self._doc_stats.clear()
        logger.info("Purged all active vector indices from memory.")

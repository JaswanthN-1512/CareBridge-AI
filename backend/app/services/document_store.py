"""In-memory transient document repository for active user sessions."""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("carebridge.document_store")


class DocumentStore:
    """Thread-safe, session-isolated in-memory document store.
    
    Holds extracted text, page structures, and metadata for uploaded documents
    during their active session without persisting sensitive health data to disk.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def save_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Store extracted document content and metadata indexed by document UUID."""
        self._store[document_id] = data
        logger.info(f"Saved document content for {document_id} ({data.get('filename', 'unknown')}).")

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored document content by document UUID."""
        return self._store.get(document_id)

    def has_document(self, document_id: str) -> bool:
        """Check if document content exists in the store."""
        return document_id in self._store

    def delete_document(self, document_id: str) -> bool:
        """Remove a document from the transient store."""
        if document_id in self._store:
            del self._store[document_id]
            logger.info(f"Purged document content for {document_id}.")
            return True
        return False

    def list_document_ids(self) -> List[str]:
        """Return all active document UUIDs."""
        return list(self._store.keys())

    def clear(self) -> None:
        """Clear all stored documents from transient memory."""
        self._store.clear()
        logger.info("Cleared all documents from in-memory document store.")


# Singleton instance
_document_store_instance = DocumentStore()


def get_document_store() -> DocumentStore:
    """Dependency provider returning the singleton document store instance."""
    return _document_store_instance

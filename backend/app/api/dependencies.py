"""FastAPI dependency providers for services and shared singletons."""

from functools import lru_cache
from app.config import get_settings
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.services.analysis_service import AnalysisService
from app.services.rag_service import RAGService
from app.services.document_store import get_document_store, DocumentStore

# Shared singletons for active session lifecycle
_shared_vector_store = VectorStoreService(get_settings())
_shared_rag_service = RAGService(vector_store_service=_shared_vector_store)
_shared_analysis_service = AnalysisService()


def get_pdf_service() -> PDFService:
    """Provide configured PDF extraction service."""
    settings = get_settings()
    return PDFService(max_size_mb=settings.MAX_UPLOAD_SIZE_MB)


def get_chunking_service() -> ChunkingService:
    """Provide configured semantic chunking service."""
    return ChunkingService()


def get_vector_store() -> VectorStoreService:
    """Provide shared VectorStoreService instance maintaining active document indices."""
    return _shared_vector_store


def get_analysis_service() -> AnalysisService:
    """Provide shared AnalysisService instance."""
    return _shared_analysis_service


def get_rag_service() -> RAGService:
    """Provide shared RAGService instance connected to active vector store."""
    return _shared_rag_service


def get_doc_store() -> DocumentStore:
    """Provide shared in-memory document store."""
    return get_document_store()

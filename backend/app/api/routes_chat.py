"""API endpoint for source-grounded conversational RAG question-answering."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.request_models import DocumentChatRequest
from app.models.response_models import DocumentChatResponse, ErrorResponse
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreServiceError
from app.api.dependencies import get_rag_service

logger = logging.getLogger("carebridge.routes_chat")
router = APIRouter(prefix="/api", tags=["Document Q&A"])


@router.post(
    "/chat",
    response_model=DocumentChatResponse,
    summary="Query Document with Grounded RAG Chatbot",
    responses={
        404: {"model": ErrorResponse, "description": "Document not found or not indexed"},
        500: {"model": ErrorResponse, "description": "RAG processing error"},
    },
)
async def chat_with_document(
    payload: DocumentChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Answer patient questions grounded strictly in the retrieved excerpts of their uploaded document.
    
    Includes verified page citations and prevents hallucinations when information is absent.
    """
    logger.info(f"Received query on document {payload.document_id}: '{payload.question[:50]}...'")

    try:
        response = rag_service.answer_question(
            document_id=payload.document_id,
            question=payload.question,
        )
        return response
    except VectorStoreServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Chat failed on {payload.document_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve an answer for this document.",
        )

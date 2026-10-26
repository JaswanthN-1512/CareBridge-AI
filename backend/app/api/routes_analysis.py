"""API endpoint for triggering multi-prompt structured document intelligence analysis."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.request_models import DocumentAnalysisRequest
from app.models.response_models import DocumentAnalysisResponse, ErrorResponse
from app.services.analysis_service import AnalysisService
from app.services.document_store import DocumentStore
from app.api.dependencies import get_analysis_service, get_doc_store

logger = logging.getLogger("carebridge.routes_analysis")
router = APIRouter(prefix="/api", tags=["Document Analysis"])


@router.post(
    "/analyze",
    response_model=DocumentAnalysisResponse,
    summary="Generate Structured Document Intelligence Report",
    responses={
        404: {"model": ErrorResponse, "description": "Document session not found"},
        500: {"model": ErrorResponse, "description": "Analysis processing failure"},
    },
)
async def analyze_document(
    payload: DocumentAnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    doc_store: DocumentStore = Depends(get_doc_store),
):
    """Generate a multi-faceted healthcare document intelligence report.
    
    Produces:
    - Executive plain-language summary
    - Key structured findings and lab measurements
    - Action checklist derived from explicit clinician notes
    - Thoughtful questions to ask the attending healthcare professional
    """
    doc_data = doc_store.get_document(payload.document_id)
    if not doc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{payload.document_id}' not found in active session. Please upload your PDF first.",
        )

    logger.info(f"Triggering structured analysis for document {payload.document_id} ({doc_data.get('filename')})...")

    try:
        analysis_report = analysis_service.analyze_document(
            document_id=payload.document_id,
            document_text=doc_data["full_text"],
            filename=doc_data.get("filename", "document.pdf"),
        )
        return analysis_report
    except Exception as exc:
        logger.error(f"Analysis failed for {payload.document_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete document analysis: {str(exc)}",
        )

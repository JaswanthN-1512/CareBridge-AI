"""API endpoint for validating, extracting, and indexing uploaded patient PDF documents."""

import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from pathlib import Path
from app.models.response_models import DocumentUploadResponse, ErrorResponse
from app.services.pdf_service import PDFService, PDFServiceError
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService, VectorStoreServiceError
from app.services.document_store import DocumentStore
from app.api.dependencies import (
    get_pdf_service,
    get_chunking_service,
    get_vector_store,
    get_doc_store,
)

logger = logging.getLogger("carebridge.routes_upload")
router = APIRouter(prefix="/api", tags=["Document Processing"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Index Clinical PDF Document",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or corrupt PDF"},
        413: {"model": ErrorResponse, "description": "File payload exceeds size limit"},
        415: {"model": ErrorResponse, "description": "Unsupported file format"},
        422: {"model": ErrorResponse, "description": "Empty or unreadable document"},
    },
)
async def upload_document(
    file: UploadFile = File(..., description="PDF document containing medical records or lab reports"),
    pdf_service: PDFService = Depends(get_pdf_service),
    chunking_service: ChunkingService = Depends(get_chunking_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    doc_store: DocumentStore = Depends(get_doc_store),
):
    """Ingest a PDF document, validate magic bytes, extract pages, chunk text, and construct vector index."""
    raw_filename = file.filename or "uploaded_document.pdf"

    # Reject null bytes, URL-encoded null bytes, or forbidden control characters
    if "\0" in raw_filename or "\x00" in raw_filename or "%00" in raw_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename containing forbidden characters.",
        )

    # Sanitize against path traversal by extracting only the terminal filename component
    filename = Path(raw_filename).name or "uploaded_document.pdf"

    # Step 1: MIME & extension check
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file format. Only PDF documents (.pdf) are accepted.",
        )

    # Step 2: Read file bytes into memory
    try:
        file_bytes = await file.read()
    except Exception as exc:
        logger.error(f"Failed to read upload stream: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file stream.",
        )

    document_id = str(uuid.uuid4())
    logger.info(f"Processing upload '{filename}' ({len(file_bytes)} bytes) -> assigned UUID {document_id}")

    # Step 3: Extract and clean document text
    try:
        extracted = pdf_service.extract_document(file_bytes=file_bytes, filename=filename)
    except PDFServiceError as exc:
        err_msg = str(exc)
        if "exceeds maximum allowed limit" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg,
        )
    except Exception as exc:
        logger.error(f"Unexpected extraction error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to process PDF: {str(exc)}",
        )

    # Step 4: Split into chunks with page metadata
    try:
        chunks = chunking_service.split_extracted_pages(
            pages=extracted["pages"],
            document_id=document_id,
            filename=filename,
        )
    except Exception as exc:
        logger.error(f"Chunking failed for {document_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process text into search chunks.",
        )

    # Step 5: Construct vector index
    try:
        vector_count = vector_store.create_index(document_id=document_id, chunks=chunks)
    except VectorStoreServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    # Step 6: Cache in transient session store
    doc_store.save_document(
        document_id=document_id,
        data={
            "document_id": document_id,
            "filename": filename,
            "file_size_bytes": len(file_bytes),
            "total_pages": extracted["total_pages"],
            "total_chunks": vector_count,
            "full_text": extracted["full_text"],
            "pages": extracted["pages"],
            "metadata": extracted["metadata"],
        },
    )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        file_size_bytes=len(file_bytes),
        total_pages=extracted["total_pages"],
        total_chunks=vector_count,
        status="indexed",
        message="Document successfully verified, extracted, and indexed into knowledge base.",
    )

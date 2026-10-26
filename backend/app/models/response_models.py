"""Pydantic response models for CareBridge AI API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response returned upon successful PDF upload, text extraction, and vector indexing."""

    document_id: str = Field(..., description="Unique UUID assigned to the indexed document.")
    filename: str = Field(..., description="Original name of the uploaded PDF file.")
    file_size_bytes: int = Field(..., description="File size in bytes.")
    total_pages: int = Field(..., description="Number of extracted pages.")
    total_chunks: int = Field(..., description="Number of text chunks generated and indexed.")
    status: str = Field(default="indexed", description="Indexing status: 'indexed', 'failed', 'processing'.")
    message: str = Field(..., description="Human-readable status summary.")


class KeyInformationItem(BaseModel):
    """Individual structured key finding or metadata attribute extracted from the document."""

    category: str = Field(
        ...,
        description="Category classification (e.g., 'Document Metadata', 'Laboratory Values', 'Instructions').",
        examples=["Laboratory Values"],
    )
    label: str = Field(
        ...,
        description="Name of the test, observation, or attribute.",
        examples=["Fasting Blood Glucose"],
    )
    value: str = Field(
        ...,
        description="Recorded value with units or descriptive finding.",
        examples=["104 mg/dL (Reference: 70-99 mg/dL)"],
    )
    source_page: Optional[int] = Field(
        default=None,
        description="Page number in the original PDF where this finding was documented.",
        examples=[1],
    )


class ActionItem(BaseModel):
    """Actionable step derived strictly from clinician directions in the document."""

    id: str = Field(..., description="Unique client identifier for the action item.")
    description: str = Field(..., description="Description of the action.")
    completed: bool = Field(default=False, description="Interactive checklist completion status.")
    source_page: Optional[int] = Field(default=None, description="Page where this instruction is documented.")


class DocumentAnalysisResponse(BaseModel):
    """Complete structured intelligence report for a patient's document."""

    document_id: str = Field(..., description="Unique UUID of the analyzed document.")
    document_type: str = Field(
        ...,
        description="Type of document (e.g., 'Discharge Summary', 'Outpatient Blood Panel', 'Radiology Report').",
    )
    summary: str = Field(
        ...,
        description="Concise, plain-language patient summary of the document contents.",
    )
    key_information: List[KeyInformationItem] = Field(
        default_factory=list,
        description="Important structured data points extracted from the document.",
    )
    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Actionable next steps explicitly stated by clinicians in the document.",
    )
    questions_for_clinician: List[str] = Field(
        default_factory=list,
        description="Patient-prepared questions to discuss at the next healthcare visit.",
    )
    safety_note: str = Field(
        default="CareBridge AI provides educational summaries and does not provide clinical diagnoses or treatment plans. Consult your healthcare professional.",
        description="Mandatory medical and informational disclaimer.",
    )


class SourceReference(BaseModel):
    """Verifiable source citation linking an answer directly to document pages and text chunks."""

    page: int = Field(..., description="Page number where the evidence is located.")
    chunk_id: Optional[int] = Field(default=None, description="ID of the retrieved text chunk.")
    snippet: str = Field(..., description="Relevant text excerpt from the document.")


class DocumentChatResponse(BaseModel):
    """Response model for source-grounded conversational RAG Q&A."""

    document_id: str = Field(..., description="Target document UUID.")
    question: str = Field(..., description="User's original query.")
    answer: str = Field(..., description="AI response grounded strictly in the retrieved context.")
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="List of verified document page citations and excerpt previews.",
    )
    is_grounded: bool = Field(
        default=True,
        description="Flag indicating whether verifiable sources were found and utilized.",
    )


class HealthResponse(BaseModel):
    """API health and operational telemetry response."""

    status: str = Field(default="healthy", description="Operational status.")
    version: str = Field(default="1.0.0", description="API version.")
    environment: str = Field(..., description="Runtime environment.")
    llm_provider: str = Field(..., description="Active LLM provider.")
    embedding_provider: str = Field(..., description="Active embeddings provider.")
    vector_store_type: str = Field(..., description="Vector store engine.")


class ErrorResponse(BaseModel):
    """Standardized error envelope returned across all API endpoints."""

    error: bool = Field(default=True, description="Always true for error responses.")
    code: str = Field(..., description="Machine-readable error code (e.g., 'INVALID_PDF').")
    message: str = Field(..., description="User-friendly error explanation.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic details.")

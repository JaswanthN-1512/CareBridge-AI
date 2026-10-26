"""Pydantic request models for CareBridge AI API endpoints."""

from pydantic import BaseModel, Field, field_validator


class DocumentAnalysisRequest(BaseModel):
    """Payload to trigger structured AI analysis for a previously uploaded document."""

    document_id: str = Field(
        ...,
        description="Unique UUID of the uploaded and indexed document.",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )


class DocumentChatRequest(BaseModel):
    """Payload for asking a question about a specific document using RAG."""

    document_id: str = Field(
        ...,
        description="Unique UUID of the target document.",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    question: str = Field(
        ...,
        description="Patient question regarding the uploaded document.",
        examples=["What does this report say about follow-up appointments?"],
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Ensure question is not empty or composed solely of whitespace."""
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Question must contain at least 2 non-whitespace characters.")
        if len(trimmed) > 1000:
            raise ValueError("Question cannot exceed 1000 characters.")
        return trimmed

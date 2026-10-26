"""Foundation verification tests for CareBridge AI backend."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import get_settings
from app.models.response_models import (
    DocumentUploadResponse,
    DocumentAnalysisResponse,
    DocumentChatResponse,
    KeyInformationItem,
    ActionItem,
    SourceReference,
)


@pytest.fixture
def client():
    """Create a FastAPI test client fixture."""
    return TestClient(app)


def test_root_endpoint(client):
    """Verify that root endpoint provides service identity and documentation link."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CareBridge AI API"
    assert data["status"] == "operational"
    assert "docs" in data


def test_health_check_endpoint(client):
    """Verify that /api/health returns operational configuration status."""
    settings = get_settings()
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["environment"] == settings.ENVIRONMENT
    assert data["llm_provider"] == settings.LLM_PROVIDER
    assert data["vector_store_type"] == settings.VECTOR_STORE_TYPE


def test_models_contract_integrity():
    """Verify that core Pydantic response models validate strict data structures."""
    upload_res = DocumentUploadResponse(
        document_id="test-doc-123",
        filename="report.pdf",
        file_size_bytes=1024,
        total_pages=2,
        total_chunks=6,
        status="indexed",
        message="Document indexed successfully.",
    )
    assert upload_res.document_id == "test-doc-123"

    analysis_res = DocumentAnalysisResponse(
        document_id="test-doc-123",
        document_type="Lab Report",
        summary="Test summary of blood chemistry.",
        key_information=[
            KeyInformationItem(
                category="Lab Values",
                label="Glucose",
                value="99 mg/dL",
                source_page=1,
            )
        ],
        action_items=[
            ActionItem(
                id="act_1",
                description="Routine follow-up in 6 months",
                completed=False,
                source_page=2,
            )
        ],
        questions_for_clinician=["Should I continue this regimen?"],
    )
    assert len(analysis_res.key_information) == 1
    assert analysis_res.action_items[0].completed is False

    chat_res = DocumentChatResponse(
        document_id="test-doc-123",
        question="What is my glucose?",
        answer="Your glucose was documented as 99 mg/dL.",
        sources=[SourceReference(page=1, chunk_id=2, snippet="Glucose: 99 mg/dL")],
        is_grounded=True,
    )
    assert chat_res.is_grounded is True
    assert chat_res.sources[0].page == 1

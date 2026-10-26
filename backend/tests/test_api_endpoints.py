"""End-to-end integration tests for FastAPI endpoints (/upload, /analyze, /chat, /samples)."""

import io
import pytest
from fastapi.testclient import TestClient
import fitz

from app.main import app


@pytest.fixture
def client():
    """Create a FastAPI TestClient fixture."""
    return TestClient(app)


def test_list_and_load_sample_documents(client):
    """Verify listing sample catalog and loading a synthetic document into an active session."""
    # 1. List samples
    list_res = client.get("/api/samples")
    assert list_res.status_code == 200
    samples = list_res.json()
    assert len(samples) >= 3
    sample_ids = [s["id"] for s in samples]
    assert "normal_metabolic_panel" in sample_ids

    # 2. Load the normal metabolic panel sample
    load_res = client.post("/api/samples/normal_metabolic_panel/load")
    assert load_res.status_code == 201
    upload_data = load_res.json()
    assert "document_id" in upload_data
    assert upload_data["status"] == "indexed"
    assert upload_data["total_pages"] == 2
    assert upload_data["total_chunks"] >= 2

    doc_id = upload_data["document_id"]

    # 3. Trigger document analysis on the loaded sample
    analysis_res = client.post("/api/analyze", json={"document_id": doc_id})
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert analysis_data["document_id"] == doc_id
    assert len(analysis_data["summary"]) > 50
    assert len(analysis_data["key_information"]) >= 2
    assert len(analysis_data["action_items"]) >= 2
    assert len(analysis_data["questions_for_clinician"]) >= 3

    # 4. Ask a grounded question in RAG chat
    chat_res = client.post(
        "/api/chat",
        json={"document_id": doc_id, "question": "What was my fasting blood glucose level?"},
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["is_grounded"] is True
    assert "glucose" in chat_data["answer"].lower()
    assert len(chat_data["sources"]) >= 1
    assert chat_data["sources"][0]["page"] == 1

    # 5. Ask an out-of-scope question
    out_of_scope_res = client.post(
        "/api/chat",
        json={"document_id": doc_id, "question": "Does this document discuss my knee replacement surgery?"},
    )
    assert out_of_scope_res.status_code == 200
    out_data = out_of_scope_res.json()
    assert out_data["is_grounded"] is False
    assert len(out_data["sources"]) == 0
    assert "couldn't find that information" in out_data["answer"].lower()


def test_multipart_pdf_upload_endpoint(client):
    """Verify uploading a binary PDF file via multipart/form-data."""
    # Generate in-memory PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Cardiology Outpatient Clinic\nBlood Pressure: 120/80 mmHg\nFollow-up in 6 months.", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()

    # Upload valid PDF
    files = {"file": ("cardio_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["filename"] == "cardio_report.pdf"
    assert data["total_pages"] == 1
    assert data["status"] == "indexed"

    doc_id = data["document_id"]

    # Verify chat works with newly uploaded document
    chat_res = client.post(
        "/api/chat",
        json={"document_id": doc_id, "question": "What does this document say about blood pressure?"},
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["is_grounded"] is True
    assert "120/80" in chat_data["answer"] or "blood pressure" in chat_data["answer"].lower()


def test_upload_invalid_mime_rejection(client):
    """Verify that non-PDF files are rejected with 415 Unsupported Media Type."""
    files = {"file": ("notes.txt", io.BytesIO(b"Hello medical text"), "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 415
    data = response.json()
    assert "pdf" in data["message"].lower()


def test_analyze_nonexistent_document_returns_404(client):
    """Verify analyzing an unknown document UUID returns structured 404."""
    response = client.post("/api/analyze", json={"document_id": "nonexistent-doc-id-999"})
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["message"].lower()

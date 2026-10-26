"""End-to-End Integration Test Suite for CareBridge AI.

Validates the full client-server lifecycle mirroring frontend interactions:
- System health & telemetry
- Synthetic sample document loading & indexing
- Multipart PDF upload & parsing
- Multi-prompt structured document intelligence analysis
- Conversational RAG querying with page citations and anti-hallucination guardrails
- Structured error envelopes and validation handling
"""

import io
import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_document_store, get_vector_store
from app.services.embedding_service import DeterministicEmbeddings
from app.services.vector_store_service import VectorStoreService


@pytest.fixture(autouse=True)
def clean_services():
    """Ensure clean isolated service state before each end-to-end test."""
    doc_store = get_document_store()
    doc_store.clear()

    # Clear active vector store collections
    vector_service = get_vector_store()
    vector_service.clear_all()
    # Inject deterministic embedder for test predictability
    vector_service.embedding_model = DeterministicEmbeddings(dimension=128)


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generate a clean synthetic clinical discharge PDF using PyMuPDF."""
    doc = fitz.open()

    # Page 1: Hospital encounter and diagnosis
    page1 = doc.new_page()
    page1.insert_text(
        (50, 60),
        "METROPOLITAN GENERAL HOSPITAL\n"
        "PATIENT DISCHARGE SUMMARY & INSTRUCTIONS\n\n"
        "Patient Name: Jane Doe    DOB: 1982-04-12    MRN: MGH-88219\n"
        "Admission Date: October 20, 2026    Discharge Date: October 24, 2026\n"
        "Attending Physician: Dr. Sarah Vance, MD (Cardiology)\n\n"
        "ADMISSION DIAGNOSIS:\n"
        "Acute hypertensive crisis with secondary essential hypertension.\n\n"
        "HOSPITAL COURSE SUMMARY:\n"
        "Patient presented to the emergency department with blood pressure 188/110 mmHg\n"
        "and severe occipital headache. Successfully stabilized using intravenous labetalol\n"
        "and transitioned to oral antihypertensive regimen. Renal ultrasound unremarkable.\n"
        "Discharged in stable condition.",
    )

    # Page 2: Prescriptions and follow-up plan
    page2 = doc.new_page()
    page2.insert_text(
        (50, 60),
        "METROPOLITAN GENERAL HOSPITAL - PAGE 2\n\n"
        "DISCHARGE MEDICATIONS:\n"
        "1. Lisinopril 20 mg oral tablet - Once daily in the morning.\n"
        "2. Amlodipine 5 mg oral tablet - Once daily in the evening.\n"
        "3. Hydrochlorothiazide 12.5 mg oral tablet - Once daily with breakfast.\n\n"
        "DISCHARGE ACTION PLAN & FOLLOW-UP:\n"
        "1. Schedule follow-up appointment with primary care physician within 7 days.\n"
        "2. Log home blood pressure twice daily (morning and evening).\n"
        "3. Follow strict low-sodium DASH dietary plan (less than 1,500 mg sodium daily).\n"
        "4. Obtain repeat Basic Metabolic Panel (BMP) serum creatinine and potassium in 14 days.\n\n"
        "WARNING SIGNS REQUIRING IMMEDIATE ATTENTION:\n"
        "Return to Emergency Department if systolic BP > 180, severe headache, or chest pain.",
    )

    pdf_buffer = io.BytesIO()
    doc.save(pdf_buffer)
    doc.close()
    return pdf_buffer.getvalue()


class TestEndToEndLifecycle:
    """Complete user journey integration tests mirroring frontend operations."""

    def test_e2e_health_check(self, client: TestClient):
        """Verify GET /api/health returns operational status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_provider" in data
        assert "embedding_provider" in data

    def test_e2e_samples_listing(self, client: TestClient):
        """Verify GET /api/samples returns benchmark demonstration documents."""
        response = client.get("/api/samples")
        assert response.status_code == 200
        samples = response.json()
        assert isinstance(samples, list)
        assert len(samples) >= 3

        # Verify essential fields for frontend rendering
        for sample in samples:
            assert "id" in sample
            assert "title" in sample
            assert "description" in sample
            assert "page_count" in sample

    def test_e2e_sample_loading_and_analysis(self, client: TestClient):
        """Verify 1-click synthetic benchmark load followed by full intelligence analysis."""
        # 1. Load sample document using valid catalog ID
        load_res = client.post("/api/samples/long_discharge_summary/load")
        assert load_res.status_code in [200, 201]
        upload_data = load_res.json()
        doc_id = upload_data["document_id"]
        assert doc_id is not None
        assert upload_data["total_pages"] >= 1
        assert upload_data["total_chunks"] >= 1

        # 2. Trigger multi-prompt analysis
        analyze_res = client.post("/api/analyze", json={"document_id": doc_id})
        assert analyze_res.status_code == 200
        analysis = analyze_res.json()

        assert analysis["document_id"] == doc_id
        assert len(analysis["summary"]) > 20
        assert isinstance(analysis["key_information"], list)
        assert len(analysis["key_information"]) > 0
        assert isinstance(analysis["action_items"], list)
        assert len(analysis["action_items"]) > 0
        assert isinstance(analysis["questions_for_clinician"], list)
        assert len(analysis["questions_for_clinician"]) > 0
        assert "safety_note" in analysis

        # 3. Chat with the sample document
        chat_res = client.post(
            "/api/chat",
            json={
                "document_id": doc_id,
                "question": "What discharge medications are prescribed?",
            },
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert chat_data["document_id"] == doc_id
        assert len(chat_data["answer"]) > 10
        assert chat_data["is_grounded"] is True
        assert len(chat_data["sources"]) > 0
        assert all("page" in s and "snippet" in s for s in chat_data["sources"])

    def test_e2e_multipart_pdf_upload_and_rag_chat(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """Verify full user upload flow: upload PDF -> analyze -> RAG query with citations."""
        # 1. Upload multipart PDF
        upload_res = client.post(
            "/api/upload",
            files={"file": ("jane_doe_discharge.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert upload_res.status_code in [200, 201]
        upload_data = upload_res.json()
        doc_id = upload_data["document_id"]
        assert upload_data["total_pages"] == 2
        assert upload_data["total_chunks"] >= 2

        # 2. Structured Analysis
        analyze_res = client.post("/api/analyze", json={"document_id": doc_id})
        assert analyze_res.status_code == 200
        report = analyze_res.json()
        assert report["document_id"] == doc_id
        assert report["summary"] is not None

        # Verify key observations extracted
        categories = [item["category"] for item in report["key_information"]]
        assert len(categories) > 0

        # 3. Grounded Question: Discharge medications
        chat_res = client.post(
            "/api/chat",
            json={
                "document_id": doc_id,
                "question": "What discharge medications are prescribed?",
            },
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert "lisinopril" in chat_data["answer"].lower() or "medication" in chat_data["answer"].lower()
        assert chat_data["is_grounded"] is True
        assert len(chat_data["sources"]) >= 1

        # Check citation points to Page 2 where medications are listed
        pages = [s["page"] for s in chat_data["sources"]]
        assert 2 in pages

        # 4. Out-of-Scope / Anti-Hallucination Question
        oos_res = client.post(
            "/api/chat",
            json={
                "document_id": doc_id,
                "question": "What is the capital of Australia?",
            },
        )
        assert oos_res.status_code == 200
        oos_data = oos_res.json()
        # Must refuse or flag ungrounded
        assert (
            oos_data["is_grounded"] is False
            or "not mentioned" in oos_data["answer"].lower()
            or "does not contain" in oos_data["answer"].lower()
        )

    def test_e2e_error_handling_and_validation(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """Verify API responds with structured error envelopes for failure modes."""
        # 1. Analyze non-existent document
        res_missing = client.post("/api/analyze", json={"document_id": "nonexistent-doc-id"})
        assert res_missing.status_code == 404
        data_missing = res_missing.json()
        assert data_missing["error"] is True
        assert "not found" in data_missing["message"].lower()

        # 2. Chat with non-existent document
        res_chat_missing = client.post(
            "/api/chat",
            json={"document_id": "nonexistent-doc-id", "question": "Hello?"},
        )
        assert res_chat_missing.status_code == 404
        assert res_chat_missing.json()["error"] is True

        # 3. Chat with empty question on an indexed document (Validation Error)
        upload_res = client.post(
            "/api/upload",
            files={"file": ("test.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert upload_res.status_code in [200, 201]
        doc_id = upload_res.json()["document_id"]

        res_empty_q = client.post(
            "/api/chat",
            json={"document_id": doc_id, "question": "   "},
        )
        assert res_empty_q.status_code in [400, 422]
        assert res_empty_q.json()["error"] is True

        # 4. Upload non-PDF file
        res_txt = client.post(
            "/api/upload",
            files={"file": ("notes.txt", b"Hello world text", "text/plain")},
        )
        assert res_txt.status_code in [400, 415]
        assert res_txt.json()["error"] is True
        assert "only pdf" in res_txt.json()["message"].lower()

"""Tests for RAGService, emergency triage, source citation formatting, and anti-hallucination guardrails."""

import pytest
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.services.rag_service import RAGService
from app.services.llm_service import MockChatModel


@pytest.fixture
def indexed_rag_setup():
    """Create an indexed multi-page medical test document."""
    chunker = ChunkingService(chunk_size=200, chunk_overlap=30)
    pages = [
        {
            "page_number": 1,
            "text": "Outpatient Metabolic Panel. Fasting Blood Glucose measured at 98 mg/dL. Total Cholesterol is 185 mg/dL.",
            "is_empty": False,
        },
        {
            "page_number": 2,
            "text": "Clinical Plan & Instructions: Follow-up visit scheduled with Endocrinology in 4 weeks. Continue morning Metformin 500mg daily.",
            "is_empty": False,
        },
    ]

    doc_id = "test-doc-rag-01"
    chunks = chunker.split_extracted_pages(pages, document_id=doc_id, filename="metabolic.pdf")

    vector_service = VectorStoreService()
    vector_service.create_index(doc_id, chunks)

    rag_service = RAGService(vector_store_service=vector_service, llm=MockChatModel())
    return rag_service, doc_id


def test_rag_emergency_triage_interception(indexed_rag_setup):
    """Verify that acute emergency keywords trigger immediate redirection without querying LLM."""
    rag_service, doc_id = indexed_rag_setup

    response = rag_service.answer_question(
        document_id=doc_id,
        question="I am having severe crushing chest pain and shortness of breath, what medicine in this report will help?",
    )

    assert response.is_grounded is False
    assert len(response.sources) == 0
    assert "URGENT SAFETY NOTICE" in response.answer
    assert "911" in response.answer


def test_rag_grounded_answer_with_citations(indexed_rag_setup):
    """Verify that a valid question generates an answer citing the exact page."""
    rag_service, doc_id = indexed_rag_setup

    response = rag_service.answer_question(
        document_id=doc_id,
        question="What does this report say about my fasting blood glucose?",
    )

    assert response.is_grounded is True
    assert "page 1" in response.answer.lower()
    assert "glucose" in response.answer.lower()
    assert len(response.sources) >= 1
    assert response.sources[0].page == 1
    assert "glucose" in response.sources[0].snippet.lower()


def test_rag_follow_up_citations_page_2(indexed_rag_setup):
    """Verify that query for follow-up directions cites Page 2."""
    rag_service, doc_id = indexed_rag_setup

    response = rag_service.answer_question(
        document_id=doc_id,
        question="When is my follow-up visit with endocrinology?",
    )

    assert response.is_grounded is True
    assert "page 2" in response.answer.lower()
    assert len(response.sources) >= 1
    assert response.sources[0].page == 2
    assert "endocrinology" in response.sources[0].snippet.lower()


def test_rag_hallucination_control_out_of_scope(indexed_rag_setup):
    """Verify that questions about topics absent from the document trigger 'information not found'."""
    rag_service, doc_id = indexed_rag_setup

    response = rag_service.answer_question(
        document_id=doc_id,
        question="What did my brain MRI scan and knee X-ray show?",
    )

    assert response.is_grounded is False
    assert len(response.sources) == 0
    assert "couldn't find that information in the uploaded document" in response.answer.lower()

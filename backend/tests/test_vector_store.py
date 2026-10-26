"""Tests for ChunkingService, EmbeddingService, and VectorStoreService."""

import pytest
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import DeterministicEmbeddings
from app.services.vector_store_service import VectorStoreService, VectorStoreServiceError


def test_chunking_service_preserves_page_metadata():
    """Verify that chunks retain accurate page numbers, document UUIDs, and sequential IDs."""
    chunker = ChunkingService(chunk_size=150, chunk_overlap=30)
    pages = [
        {
            "page_number": 1,
            "text": "Comprehensive Metabolic Panel report. Patient fasting blood glucose is 94 mg/dL. Calcium is 9.2 mg/dL.",
            "is_empty": False,
        },
        {
            "page_number": 2,
            "text": "Clinician Discharge Notes: Follow-up visit scheduled with Cardiology in three weeks. Continue current regimen.",
            "is_empty": False,
        },
        {
            "page_number": 3,
            "text": "   ",
            "is_empty": True,
        },
    ]

    chunks = chunker.split_extracted_pages(pages, document_id="doc-abc-123", filename="panel.pdf")

    assert len(chunks) >= 2
    # Check page 1 chunk metadata
    p1_chunks = [c for c in chunks if c.metadata["page"] == 1]
    assert len(p1_chunks) >= 1
    assert "glucose" in p1_chunks[0].page_content.lower()
    assert p1_chunks[0].metadata["document_id"] == "doc-abc-123"
    assert p1_chunks[0].metadata["filename"] == "panel.pdf"

    # Check page 2 chunk metadata
    p2_chunks = [c for c in chunks if c.metadata["page"] == 2]
    assert len(p2_chunks) >= 1
    assert "cardiology" in p2_chunks[0].page_content.lower()

    # Empty page 3 should yield 0 chunks
    p3_chunks = [c for c in chunks if c.metadata["page"] == 3]
    assert len(p3_chunks) == 0


def test_deterministic_embeddings_reproducibility():
    """Verify that offline deterministic embeddings generate unit vectors and calculate similarity."""
    embedder = DeterministicEmbeddings(dimension=128)
    vec1 = embedder.embed_query("fasting blood glucose 94 mg/dL")
    vec2 = embedder.embed_query("fasting blood glucose 94 mg/dL")
    vec3 = embedder.embed_query("unrelated orthopedic knee arthroscopy instructions")

    assert len(vec1) == 128
    assert vec1 == vec2  # Exact reproducibility

    # Dot product of identical unit vectors should equal ~1.0
    dot_similar = sum(a * b for a, b in zip(vec1, vec2))
    assert abs(dot_similar - 1.0) < 1e-4

    # Dot product with unrelated text should be significantly lower
    dot_unrelated = sum(a * b for a, b in zip(vec1, vec3))
    assert dot_unrelated < 0.5


def test_vector_store_index_and_similarity_retrieval():
    """Verify creating an index, querying top chunks, and purging per-document stores."""
    chunker = ChunkingService(chunk_size=200, chunk_overlap=20)
    pages = [
        {
            "page_number": 1,
            "text": "Laboratory Section: Serum Creatinine measured at 0.9 mg/dL. eGFR is greater than 60.",
            "is_empty": False,
        },
        {
            "page_number": 2,
            "text": "Medication Section: Lisinopril 10mg daily prescribed for blood pressure maintenance.",
            "is_empty": False,
        },
    ]

    chunks = chunker.split_extracted_pages(pages, document_id="doc-xyz-789", filename="labs.pdf")

    vector_service = VectorStoreService()
    count = vector_service.create_index("doc-xyz-789", chunks)
    assert count == len(chunks)
    assert vector_service.has_index("doc-xyz-789") is True
    assert vector_service.get_chunk_count("doc-xyz-789") == count

    # Search for creatinine
    results = vector_service.similarity_search_with_score("doc-xyz-789", "What is my creatinine?", k=2)
    assert len(results) > 0
    top_doc, score = results[0]
    assert "creatinine" in top_doc.page_content.lower()
    assert top_doc.metadata["page"] == 1

    # Search for medications
    results_med = vector_service.similarity_search_with_score("doc-xyz-789", "Lisinopril medication", k=2)
    assert len(results_med) > 0
    top_med_doc, _ = results_med[0]
    assert "lisinopril" in top_med_doc.page_content.lower()
    assert top_med_doc.metadata["page"] == 2

    # Querying nonexistent doc should raise VectorStoreServiceError
    with pytest.raises(VectorStoreServiceError):
        vector_service.similarity_search_with_score("nonexistent-doc-id", "question")

    # Purge index
    assert vector_service.delete_index("doc-xyz-789") is True
    assert vector_service.has_index("doc-xyz-789") is False

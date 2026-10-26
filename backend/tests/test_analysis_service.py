"""Tests for AnalysisService, multi-prompt orchestration, and structured output parsing."""

import pytest
from app.services.analysis_service import AnalysisService, clean_json_response
from app.models.response_models import DocumentAnalysisResponse


def test_clean_json_response_helper():
    """Verify clean_json_response strips markdown code fences and extraneous whitespace."""
    raw_fenced = "```json\n[{\"category\": \"Lab\", \"label\": \"Glucose\", \"value\": \"95\"}]\n```"
    cleaned = clean_json_response(raw_fenced)
    assert cleaned == '[{"category": "Lab", "label": "Glucose", "value": "95"}]'

    raw_plain = '[{"item": 1}]'
    assert clean_json_response(raw_plain) == '[{"item": 1}]'


def test_analysis_service_extracts_structured_report():
    """Verify that AnalysisService produces a fully populated DocumentAnalysisResponse from clinical text."""
    sample_text = (
        "--- [Page 1] ---\n"
        "Metabolic Health Diagnostic Laboratory\n"
        "Date: 2026-10-14\n"
        "Patient: Jane Doe | DOB: 1982-05-12\n\n"
        "TEST RESULTS:\n"
        "Fasting Blood Glucose: 104 mg/dL (70-99 mg/dL)\n"
        "Serum Creatinine: 0.9 mg/dL (0.6-1.3 mg/dL)\n"
        "Total Cholesterol: 195 mg/dL (<200 mg/dL)\n\n"
        "--- [Page 2] ---\n"
        "CLINICIAN DISCHARGE NOTES & PLAN:\n"
        "1. Schedule follow-up appointment with primary care physician in 3 months.\n"
        "2. Repeat fasting glucose panel prior to next appointment.\n"
        "3. Maintain 30 minutes of daily cardiovascular exercise.\n"
    )

    analyzer = AnalysisService()
    report = analyzer.analyze_document(
        document_id="test-doc-analysis-01",
        document_text=sample_text,
        filename="metabolic_report.pdf",
    )

    assert isinstance(report, DocumentAnalysisResponse)
    assert report.document_id == "test-doc-analysis-01"

    # Verify document type
    assert "metabolic" in report.document_type.lower() or "laboratory" in report.document_type.lower()

    # Verify summary
    assert len(report.summary) > 50
    assert "educational" not in report.summary.lower()  # Disclaimers are in safety_note

    # Verify key information extraction
    assert len(report.key_information) >= 2
    labels = [item.label.lower() for item in report.key_information]
    assert any("glucose" in l for l in labels)
    assert any("creatinine" in l for l in labels)

    # Verify action checklist
    assert len(report.action_items) >= 2
    for action in report.action_items:
        assert action.completed is False
        assert len(action.description) > 5

    # Verify clinician questions
    assert len(report.questions_for_clinician) >= 3
    for q in report.questions_for_clinician:
        assert "?" in q

    # Verify safety disclaimer
    assert "does not provide clinical diagnoses" in report.safety_note

"""API endpoints for listing and loading synthetic demonstration benchmark documents."""

import os
import uuid
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import fitz  # PyMuPDF

from app.models.response_models import DocumentUploadResponse, ErrorResponse
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.services.document_store import DocumentStore
from app.api.dependencies import (
    get_pdf_service,
    get_chunking_service,
    get_vector_store,
    get_doc_store,
)

logger = logging.getLogger("carebridge.routes_samples")
router = APIRouter(prefix="/api/samples", tags=["Sample Documents"])

# Catalog of synthetic test documents with pre-defined clinical text
SAMPLE_CATALOG: Dict[str, Dict[str, Any]] = {
    "normal_metabolic_panel": {
        "id": "normal_metabolic_panel",
        "title": "Comprehensive Metabolic & Lipid Panel",
        "filename": "sample_normal_lab_report.pdf",
        "description": "Routine outpatient blood chemistry report with normal and slightly borderline values.",
        "pages": [
            (
                "CAREBRIDGE REGIONAL HEALTH SYSTEM — OUTPATIENT DIAGNOSTIC LABORATORY\n"
                "Report Date: October 14, 2026 | Patient ID: PT-847291 | Ordering Physician: Dr. Sarah Jenkins, MD\n"
                "Specimen Collected: 2026-10-14 07:30 AM | Fasting: Yes (12 Hours)\n\n"
                "COMPREHENSIVE METABOLIC PANEL (SERUM):\n"
                "Test Name                 Observed Value     Reference Interval     Status\n"
                "Fasting Blood Glucose     104 mg/dL          70 - 99 mg/dL          BORDERLINE HIGH\n"
                "Blood Urea Nitrogen (BUN) 16 mg/dL           7 - 20 mg/dL           NORMAL\n"
                "Serum Creatinine          0.9 mg/dL          0.6 - 1.3 mg/dL        NORMAL\n"
                "eGFR                      >60 mL/min/1.73m2  >60 mL/min/1.73m2      NORMAL\n"
                "Sodium                    140 mmol/L         136 - 145 mmol/L       NORMAL\n"
                "Potassium                 4.3 mmol/L         3.5 - 5.1 mmol/L       NORMAL\n"
                "Chloride                  102 mmol/L         98 - 107 mmol/L        NORMAL\n"
                "Carbon Dioxide (CO2)      25 mmol/L          22 - 29 mmol/L         NORMAL\n"
                "Calcium                   9.4 mg/dL          8.6 - 10.2 mg/dL       NORMAL\n"
                "Total Bilirubin           0.7 mg/dL          0.2 - 1.2 mg/dL        NORMAL\n"
                "Aspartate Transferase(AST)22 U/L             10 - 40 U/L            NORMAL\n"
                "Alanine Transferase (ALT) 28 U/L             7 - 56 U/L             NORMAL\n"
            ),
            (
                "LIPID PROFILE EVALUATION (FASTING):\n"
                "Total Cholesterol         194 mg/dL          < 200 mg/dL            NORMAL\n"
                "Triglycerides             142 mg/dL          < 150 mg/dL            NORMAL\n"
                "HDL Cholesterol           52 mg/dL           > 40 mg/dL             DESIRABLE\n"
                "LDL Cholesterol (Calc)    114 mg/dL          < 100 mg/dL            BORDERLINE ELEVATED\n\n"
                "ORDERING CLINICIAN DIRECTIVES & RECOMMENDATIONS:\n"
                "1. Fasting glucose is mildly above standard threshold (104 mg/dL). Repeat fasting glucose and HbA1c in 3 months.\n"
                "2. Patient advised to maintain routine Mediterranean-style dietary pattern and engage in 30 minutes of daily walking.\n"
                "3. Follow-up consultation scheduled with Dr. Jenkins at the Outpatient Health Center on January 15, 2027 at 10:00 AM.\n"
                "4. Continue current multivitamin daily. No acute prescription alterations indicated at this time.\n"
            ),
        ],
    },
    "long_discharge_summary": {
        "id": "long_discharge_summary",
        "title": "Hospital Inpatient Discharge Summary",
        "filename": "sample_long_discharge_summary.pdf",
        "description": "Multi-page post-operative inpatient summary with surgical details, discharge medications, and follow-up care.",
        "pages": [
            (
                "ST. JUDE MEMORIAL HOSPITAL — DEPARTMENT OF SURGICAL SERVICES\n"
                "INPATIENT DISCHARGE SUMMARY\n"
                "Admission Date: October 10, 2026 | Discharge Date: October 13, 2026\n"
                "Attending Physician: Dr. Robert Martinez, MD, FACS | Department: General Surgery\n\n"
                "PRINCIPAL DISCHARGE DIAGNOSIS:\n"
                "Acute uncomplicated appendicitis (ICD-10 K35.80)\n\n"
                "PROCEDURES PERFORMED:\n"
                "Laparoscopic appendectomy performed on October 10, 2026 without perioperative complication.\n"
                "Surgeon: Dr. Robert Martinez, MD. Operative findings confirmed uncomplicated acute phlegmonous appendicitis.\n"
            ),
            (
                "HOSPITAL COURSE:\n"
                "Patient was admitted via the Emergency Department with acute right lower quadrant abdominal pain and low-grade pyrexia. "
                "Diagnostic ultrasound confirmed acute appendiceal inflammation. The patient was taken to the operating suite on the evening of admission. "
                "Post-operatively, the patient tolerated oral rehydration on Post-Operative Day 1 and advanced to a soft regular diet by Day 2. "
                "Pain was well controlled with oral acetaminophen and short-term ibuprofen. Vital signs upon discharge were stable: BP 124/78, HR 72, Afebrile.\n"
            ),
            (
                "DISCHARGE MEDICATIONS:\n"
                "1. Acetaminophen 500 mg: Take 1-2 tablets by mouth every 6 hours as needed for mild-to-moderate incision discomfort.\n"
                "2. Ibuprofen 400 mg: Take 1 tablet by mouth every 8 hours with food for inflammation (maximum 3 days).\n"
                "3. Lisinopril 10 mg: Resume chronic morning dose for routine blood pressure management.\n\n"
                "DISCHARGE INSTRUCTIONS & ACTIVITY RESTRICTIONS:\n"
                "1. Keep surgical laparoscopic incision sites clean and dry. May shower after 48 hours; no tub baths or swimming for 2 weeks.\n"
                "2. Physical restriction: No heavy lifting greater than 15 pounds for 4 weeks.\n"
                "3. Follow-up appointment: Scheduled with Dr. Martinez in the Surgical Outpatient Suite on October 27, 2026 at 2:30 PM for wound evaluation.\n"
                "4. Warning signs: Call clinic or seek immediate evaluation for fever > 101F, worsening abdominal pain, or redness/discharge at incision sites.\n"
            ),
        ],
    },
    "noisy_unformatted_report": {
        "id": "noisy_unformatted_report",
        "title": "Irregularly Formatted Encounter Report",
        "filename": "sample_noisy_unformatted_report.pdf",
        "description": "Clinical document with non-standard line wraps, uppercase labels, and inconsistent spacing.",
        "pages": [
            (
                "OUTPATIENT ENCOUNTER NOTE   *** CONFIDENTIAL CLINICAL DRAFT ***\n"
                "PT ID: 9028114       DATE OF VISIT: 2026/09/28\n"
                "PROVIDER: DR EMILY CHEN     CLINIC: COMMUNITY HEALTH ASSOCIATES\n\n"
                "CHIEF COMPLAINT: ANNUAL ROUTINE HEALTH MAINTENANCE\n"
                "VITALS: BP 128/82 MMHG   PULSE 74 BPM   WEIGHT 168 LBS   BMI 25.4\n\n"
                "ASSESSMENT / NOTES:\n"
                "PATIENT APPEARS WELL NOURISHED AND IN NO ACUTE DISTRESS.\n"
                "CARDIAC EXAM DEMONSTRATES REGULAR RATE AND RHYTHM WITHOUT MURMUR.\n"
                "LUNGS CLEAR TO AUSCULTATION BILATERALLY.\n\n"
                "DIRECTED RECOMMENDATIONS:\n"
                "- REPEAT SCREENING LIPID PANEL IN 6 MONTHS (MARCH 2027)\n"
                "- CONTINUE CURRENT EXERCISE PROGRAM 150 MINUTES WEEKLY\n"
                "- FOLLOW UP IN 1 YEAR FOR ANNUAL PREVENTIVE EXAM\n"
            )
        ],
    },
    "complex_table_report": {
        "id": "complex_table_report",
        "title": "Dense Laboratory Hematology Panel",
        "filename": "sample_complex_table_report.pdf",
        "description": "Multi-column CBC with differential and iron indices demonstrating dense tabular parsing.",
        "pages": [
            (
                "BIO-ANALYTIC REFERENCE LABORATORIES — HEMATOLOGY REPORT\n"
                "Specimen ID: LAB-2026-90184 | Collection: 2026-10-18 08:15 AM\n"
                "Patient: Arthur Pendelton | Age: 54 | Physician: Dr. Laura Sterling, MD\n\n"
                "COMPLETE BLOOD COUNT (CBC) WITH FIVE-PART AUTOMATED DIFFERENTIAL:\n"
                "Test Description            Result    Ref Range     Units      Status\n"
                "White Blood Cells (WBC)     6.8       4.5 - 11.0    x10^3/uL   NORMAL\n"
                "Red Blood Cells (RBC)       4.82      4.30 - 5.90   x10^6/uL   NORMAL\n"
                "Hemoglobin (Hgb)            14.6      13.5 - 17.5   g/dL       NORMAL\n"
                "Hematocrit (Hct)            43.8      41.0 - 50.0   %          NORMAL\n"
                "Platelet Count              248       150 - 450     x10^3/uL   NORMAL\n"
                "Neutrophils (%)             58.4      40.0 - 70.0   %          NORMAL\n"
                "Lymphocytes (%)             31.2      20.0 - 45.0   %          NORMAL\n"
                "Monocytes (%)               6.8       2.0 - 10.0    %          NORMAL\n"
            ),
            (
                "BIO-ANALYTIC REFERENCE LABORATORIES — HEMATOLOGY REPORT (PAGE 2)\n"
                "SERUM IRON INDICES & FERRITIN PANEL:\n"
                "Test Description            Result    Ref Range     Units      Status\n"
                "Total Serum Iron            88        60 - 170      ug/dL      NORMAL\n"
                "Total Iron Binding Capacity 310       250 - 425     ug/dL      NORMAL\n"
                "Transferrin Saturation      28.4      20.0 - 50.0   %          NORMAL\n"
                "Serum Ferritin              145       30 - 400      ng/mL      NORMAL\n\n"
                "PATHOLOGIST INTERPRETATION:\n"
                "All cellular indices within healthy physiologic baseline. No evidence of anemia."
            ),
        ],
    },
    "irrelevant_sections_report": {
        "id": "irrelevant_sections_report",
        "title": "Clinical Encounter with Boilerplate Sections",
        "filename": "sample_irrelevant_sections_report.pdf",
        "description": "Clinical cardiology notes mixed with administrative billing rules and parking policies.",
        "pages": [
            (
                "MEMORIAL VALLEY MEDICAL CENTER — FACILITY POLICY & ADMINISTRATIVE DISCLOSURES\n"
                "VISITOR PARKING & GARAGE RATES:\n"
                "Visitor parking is available in Garage B. First 2 hours complimentary. Hours 3-4: $4.00.\n"
                "BILLING POLICY & FINANCIAL ARBITRATION NOTICE:\n"
                "All patient accounts are managed subject to federal Truth-in-Lending regulations.\n"
                "CAFETERIA & DINING AMENITIES:\n"
                "The Evergreen Dining Pavilion is located on Floor 1, open 6:30 AM to 8:00 PM daily."
            ),
            (
                "MEMORIAL VALLEY HEART & VASCULAR INSTITUTE — CLINICAL CONSULTATION NOTE\n"
                "Patient: Gregory Vance | DOB: 1965-03-14 (Age: 61) | Date: 2026-10-16\n"
                "Attending Cardiologist: Dr. Raymond Holt, MD, FACC\n\n"
                "CLINICAL IMPRESSION & ECHOCARDIOGRAM FINDINGS:\n"
                "Transthoracic echocardiogram demonstrates normal left ventricular systolic function\n"
                "with calculated ejection fraction of 60-65%. No regional wall motion abnormalities.\n\n"
                "CURRENT CARDIAC MEDICATIONS:\n"
                "1. Metoprolol Succinate ER 25 mg: Take 1 tablet daily by mouth.\n"
                "2. Atorvastatin 20 mg: Take 1 tablet daily at bedtime.\n\n"
                "ACTION PLAN: Maintain blood pressure log. Follow-up in 6 months on April 16, 2027."
            ),
        ],
    },
}


def build_synthetic_pdf(pages_text: List[str]) -> bytes:
    """Helper to assemble a genuine in-memory PDF binary stream using PyMuPDF."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 72), text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@router.get(
    "",
    summary="List Available Synthetic Benchmark Documents",
)
async def list_sample_documents():
    """Retrieve catalog of synthetic clinical demonstration documents."""
    return [
        {
            "id": sample["id"],
            "title": sample["title"],
            "filename": sample["filename"],
            "description": sample["description"],
            "page_count": len(sample["pages"]),
        }
        for sample in SAMPLE_CATALOG.values()
    ]


@router.post(
    "/{sample_id}/load",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Load and Index Synthetic Benchmark Document",
    responses={
        404: {"model": ErrorResponse, "description": "Sample not found"},
    },
)
async def load_sample_document(
    sample_id: str,
    pdf_service: PDFService = Depends(get_pdf_service),
    chunking_service: ChunkingService = Depends(get_chunking_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    doc_store: DocumentStore = Depends(get_doc_store),
):
    """Instantly build and index a synthetic benchmark document for immediate evaluation."""
    sample = SAMPLE_CATALOG.get(sample_id)
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample document '{sample_id}' not found in benchmark catalog.",
        )

    # Read physical sample file if present, otherwise generate from synthetic text
    filename = sample["filename"]
    sample_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_documents", filename)
    )
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            pdf_bytes = f.read()
    else:
        pdf_bytes = build_synthetic_pdf(sample["pages"])

    document_id = str(uuid.uuid4())

    logger.info(f"Loading synthetic demo '{sample_id}' -> document_id {document_id}")

    # Extract, Chunk, Index
    extracted = pdf_service.extract_document(pdf_bytes, filename=filename)
    chunks = chunking_service.split_extracted_pages(extracted["pages"], document_id, filename)
    vector_count = vector_store.create_index(document_id, chunks)

    doc_store.save_document(
        document_id=document_id,
        data={
            "document_id": document_id,
            "filename": filename,
            "file_size_bytes": len(pdf_bytes),
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
        file_size_bytes=len(pdf_bytes),
        total_pages=extracted["total_pages"],
        total_chunks=vector_count,
        status="indexed",
        message=f"Sample '{sample['title']}' loaded and indexed successfully.",
    )

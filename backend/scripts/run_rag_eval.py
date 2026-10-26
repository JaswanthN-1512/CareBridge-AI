"""Evaluation script testing the 8 target RAG questions against the synthetic laboratory report."""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import fitz
from starlette.testclient import TestClient
from app.main import app

# Target PDF path check
user_pdf_path = Path(r"C:\Users\jaswa\.gemini\antigravity-ide\brain\99a278b3-02a4-42db-9994-7eaeea56eefc\.user_uploaded\media_1793007616337.pdf")

def get_synthetic_pdf_bytes() -> bytes:
    if user_pdf_path.exists():
        print(f"Loading user uploaded PDF from: {user_pdf_path}")
        return user_pdf_path.read_bytes()
    
    print("Generating synthetic laboratory PDF matching exact specification...")
    doc = fitz.open()
    
    p1 = doc.new_page()
    p1.insert_text(
        (40, 50),
        "SYNTHETIC LABORATORY REPORT\n"
        "CareBridge AI — Test Document | NOT A REAL PATIENT RECORD\n"
        "Patient ID CB-DEMO-001\n"
        "Patient Name Arun Kumar (Synthetic)\n"
        "Age / Sex 42 years / Male\n"
        "Report Date 26 October 2026\n"
        "Referring Department General Medicine\n\n"
        "Complete Blood Count (CBC)\n"
        "Test Result Reference Range Unit\n"
        "Hemoglobin 13.8 13.0 – 17.0 g/dL\n"
        "Total WBC Count 7,200 4,000 – 11,000 cells/µL\n"
        "Platelet Count 248,000 150,000 – 450,000 cells/µL\n"
        "RBC Count 4.72 4.5 – 5.9 million/µL\n"
        "Hematocrit 41.5 40 – 50 %\n\n"
        "Basic Metabolic Panel\n"
        "Test Result Reference Range Unit\n"
        "Fasting Glucose 96 70 – 99 mg/dL\n"
        "Creatinine 0.92 0.7 – 1.3 mg/dL\n"
        "Sodium 139 135 – 145 mmol/L\n"
        "Potassium 4.2 3.5 – 5.1 mmol/L\n"
        "ALT 29 7 – 56 U/L\n\n"
        "Additional Notes\n"
        "• The laboratory values above are synthetic and created only for software testing and demonstration.\n"
        "• The report contains no real patient's personal or medical information.\n"
        "• A follow-up consultation with the referring clinician is listed as recommended within 14 days.\n"
        "• The document does not contain a diagnosis or medication prescription.\n\n"
        "CareBridge Test Prompts\n"
        "• What is the hemoglobin value in this report?\n"
        "• What follow-up instruction is mentioned?\n"
        "• List the laboratory tests and their reported values.\n"
        "• Is a diagnosis mentioned in the document?\n",
        fontsize=10,
    )

    p2 = doc.new_page()
    p2.insert_text(
        (40, 50),
        "• What medication is prescribed?\n"
        "• What is the patient's home address?\n\n"
        "Safety note: This synthetic document is for testing document extraction, retrieval, summarization, and grounded question answering. "
        "It is not medical advice and should not be used for clinical decisions.\n",
        fontsize=10,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def run_evaluation():
    pdf_bytes = get_synthetic_pdf_bytes()
    client = TestClient(app)

    # Upload document
    upload_res = client.post(
        "/api/upload",
        files={"file": ("synthetic_laboratory_report.pdf", pdf_bytes, "application/pdf")},
    )
    if upload_res.status_code != 201:
        print("Upload failed:", upload_res.text)
        return

    upload_data = upload_res.json()
    doc_id = upload_data["document_id"]
    print(f"Uploaded successfully! Document ID: {doc_id}")
    print(f"Total pages: {upload_data['total_pages']}, Total chunks: {upload_data['total_chunks']}\n")

    test_cases = [
        {
            "id": 1,
            "question": "What is the creatinine value?",
            "expected": "0.92 mg/dL",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "0.92" in ans and "mg/dl" in ans.lower() and grd is True,
        },
        {
            "id": 2,
            "question": "What is the hemoglobin value?",
            "expected": "13.8 g/dL",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "13.8" in ans and "g/dl" in ans.lower() and grd is True,
        },
        {
            "id": 3,
            "question": "What is the platelet count?",
            "expected": "248,000 cells/µL",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "248,000" in ans and grd is True,
        },
        {
            "id": 4,
            "question": "What is the fasting glucose?",
            "expected": "96 mg/dL",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "96" in ans and "mg/dl" in ans.lower() and grd is True,
        },
        {
            "id": 5,
            "question": "What follow-up instruction is mentioned?",
            "expected": "Follow-up consultation within 14 days",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "14 days" in ans.lower() and grd is True,
        },
        {
            "id": 6,
            "question": "Is a diagnosis mentioned?",
            "expected": "No diagnosis is mentioned in the document.",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: "no diagnosis" in ans.lower() and grd is True,
        },
        {
            "id": 7,
            "question": "What medication is prescribed?",
            "expected": "No medication prescription is present in the document.",
            "expected_page": 1,
            "expected_grounded": True,
            "validate": lambda ans, src, grd: ("no medication" in ans.lower() or "not contain" in ans.lower()) and grd is True,
        },
        {
            "id": 8,
            "question": "What is the patient's home address?",
            "expected": "The information is not present in the document.",
            "expected_page": None,
            "expected_grounded": False,
            "validate": lambda ans, src, grd: ("not present" in ans.lower() or "couldn't find" in ans.lower()) and grd is False and len(src) == 0,
        },
    ]

    all_passed = True
    results = []

    for tc in test_cases:
        res = client.post(
            "/api/chat",
            json={"document_id": doc_id, "question": tc["question"]},
        )
        assert res.status_code == 200, f"Chat failed for Q: {tc['question']}"
        data = res.json()

        actual_ans = data["answer"]
        sources = data["sources"]
        is_grounded = data["is_grounded"]
        source_page = sources[0]["page"] if sources else None
        source_snippet = sources[0]["snippet"] if sources else "None"

        is_pass = tc["validate"](actual_ans, sources, is_grounded)
        if not is_pass:
            all_passed = False

        results.append({
            "id": tc["id"],
            "question": tc["question"],
            "expected": tc["expected"],
            "actual": actual_ans,
            "source_page": source_page,
            "source_snippet": source_snippet,
            "is_grounded": is_grounded,
            "status": "PASS" if is_pass else "FAIL",
        })

    print("=" * 100)
    print("CHAT/RAG EVALUATION RESULTS")
    print("=" * 100)
    for r in results:
        print(f"QUESTION {r['id']}: {r['question']}")
        print(f"EXPECTED ANSWER: {r['expected']}")
        print(f"RETRIEVED CHUNKS / SNIPPET: {r['source_snippet']}")
        print(f"ACTUAL ANSWER: {r['actual']}")
        print(f"SOURCE PAGE: {r['source_page']}")
        print(f"is_grounded: {r['is_grounded']}")
        print(f"RESULT: {r['status']}")
        print("-" * 100)

    print(f"\nFINAL STATUS: {'ALL TESTS PASSED (8/8)!' if all_passed else 'SOME TESTS FAILED'}\n")

if __name__ == "__main__":
    run_evaluation()

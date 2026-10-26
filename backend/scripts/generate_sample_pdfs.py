"""Synthetic Benchmark PDF Generator for CareBridge AI.

Generates the 5 canonical demonstration medical PDFs defined in Section 22:
1. sample_normal_lab_report.pdf (Clean 2-page CMP + Lipid Panel)
2. sample_long_discharge_summary.pdf (Multi-page post-operative surgical discharge)
3. sample_noisy_unformatted_report.pdf (Ragged line wraps, uppercase labels, irregular spacing)
4. sample_complex_table_report.pdf (Dense multi-column CBC with Differential tables)
5. sample_irrelevant_sections_report.pdf (Lengthy billing/parking boilerplate mixed with clinical cardiology notes)
"""

import os
import fitz  # PyMuPDF


def create_normal_lab_report() -> bytes:
    """TEST 1: Clean 2-page outpatient metabolic chemistry report."""
    doc = fitz.open()

    # Page 1: CMP
    page1 = doc.new_page()
    page1.insert_text(
        (40, 50),
        "CAREBRIDGE REGIONAL HEALTH SYSTEM — OUTPATIENT DIAGNOSTIC LABORATORY\n"
        "CLIA Certificate: #99D0876543 | Medical Director: Arthur Miller, MD, FCAP\n"
        "================================================================================\n\n"
        "PATIENT DEMOGRAPHICS & ENCOUNTER DATA:\n"
        "Patient Name: Elena Rodriguez        DOB: 1985-06-22 (Age: 41)       Sex: Female\n"
        "Patient ID: PT-847291                Encounter Date: 2026-10-14      Fasting: 12 Hours\n"
        "Ordering Physician: Dr. Sarah Jenkins, MD (Family Medicine)\n\n"
        "COMPREHENSIVE METABOLIC PANEL (SERUM):\n"
        "Analyte                     Result      Reference Interval   Units      Clinical Flag\n"
        "--------------------------------------------------------------------------------\n"
        "Fasting Blood Glucose       104         70 - 99              mg/dL      BORDERLINE HIGH\n"
        "Blood Urea Nitrogen (BUN)   16          7 - 20               mg/dL      NORMAL\n"
        "Serum Creatinine            0.9         0.6 - 1.3            mg/dL      NORMAL\n"
        "eGFR (CKD-EPI)              >60         >60                  mL/min     NORMAL\n"
        "Serum Sodium                140         136 - 145            mmol/L     NORMAL\n"
        "Serum Potassium             4.3         3.5 - 5.1            mmol/L     NORMAL\n"
        "Serum Chloride              102         98 - 107             mmol/L     NORMAL\n"
        "Carbon Dioxide (CO2)        25          22 - 29              mmol/L     NORMAL\n"
        "Serum Calcium               9.4         8.6 - 10.2           mg/dL      NORMAL\n"
        "Total Bilirubin             0.7         0.2 - 1.2            mg/dL      NORMAL\n"
        "Aspartate Transferase (AST) 22          10 - 40              U/L        NORMAL\n"
        "Alanine Transferase (ALT)   28          7 - 56               U/L        NORMAL\n\n"
        "Page 1 of 2 — Continued on next page...",
        fontsize=9,
    )

    # Page 2: Lipid Panel + Directives
    page2 = doc.new_page()
    page2.insert_text(
        (40, 50),
        "CAREBRIDGE REGIONAL HEALTH SYSTEM — OUTPATIENT DIAGNOSTIC LABORATORY\n"
        "Patient: Elena Rodriguez | ID: PT-847291 | Specimen Date: 2026-10-14\n"
        "================================================================================\n\n"
        "LIPID PROFILE EVALUATION (FASTING SERUM):\n"
        "Analyte                     Result      Target Range         Units      Clinical Flag\n"
        "--------------------------------------------------------------------------------\n"
        "Total Cholesterol           194         < 200                mg/dL      NORMAL\n"
        "Triglycerides               142         < 150                mg/dL      NORMAL\n"
        "HDL Cholesterol             52          > 40                 mg/dL      DESIRABLE\n"
        "LDL Cholesterol (Calc)      114         < 100                mg/dL      BORDERLINE ELEVATED\n\n"
        "ORDERING CLINICIAN DIRECTIVES & ACTION PLAN:\n"
        "1. Fasting blood glucose is mildly elevated at 104 mg/dL. Repeat fasting blood glucose\n"
        "   and perform screening HbA1c in 3 months.\n"
        "2. Mild LDL elevation (114 mg/dL). Initiate Mediterranean dietary pattern with reduced\n"
        "   saturated fats and maintain 30 minutes of aerobic physical activity daily.\n"
        "3. Continue existing daily multivitamin. No prescription medications required at present.\n"
        "4. Follow-up clinic appointment scheduled with Dr. Sarah Jenkins on January 15, 2027\n"
        "   at 10:00 AM at the Outpatient Health Pavilion.\n\n"
        "CRITICAL CONTACT INFORMATION:\n"
        "For urgent questions regarding these laboratory results, contact clinic desk at (555) 019-2831.\n"
        "In a life-threatening medical emergency, call 911 immediately.",
        fontsize=9,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_long_discharge_summary() -> bytes:
    """TEST 2: Multi-page post-operative inpatient surgical discharge summary."""
    doc = fitz.open()

    # Page 1: Admission & Surgical Details
    page1 = doc.new_page()
    page1.insert_text(
        (40, 50),
        "ST. JUDE MEMORIAL HOSPITAL — DEPARTMENT OF SURGICAL SERVICES\n"
        "INPATIENT DISCHARGE SUMMARY & INSTRUCTIONS\n"
        "================================================================================\n\n"
        "PATIENT IDENTIFICATION:\n"
        "Patient: Marcus Thorne               DOB: 1978-11-04 (Age: 48)       Sex: Male\n"
        "MRN: SJM-774912                      Admission Date: 2026-10-10      Discharge Date: 2026-10-13\n"
        "Attending Surgeon: Dr. Robert Martinez, MD, FACS | Service: General Surgery\n\n"
        "PRINCIPAL DIAGNOSIS UPON DISCHARGE:\n"
        "Acute uncomplicated appendicitis (ICD-10 K35.80)\n\n"
        "PROCEDURES PERFORMED:\n"
        "Laparoscopic appendectomy performed on October 10, 2026 under general anesthesia.\n"
        "Operative findings: Acute phlegmonous non-perforated appendicitis. Appendix successfully\n"
        "transected at base with laparoscopic stapler. Minimal blood loss (<15 mL). Pathologic\n"
        "specimen forwarded for routine histology.\n\n"
        "HOSPITAL COURSE:\n"
        "Patient presented via the Emergency Department with severe right lower quadrant pain\n"
        "and low-grade fever. Abdominal ultrasound confirmed non-perforated appendicitis.\n"
        "Surgery proceeded uneventfully. Post-operatively, patient was transitioned to oral liquids\n"
        "on Post-Operative Day 1 and regular low-fat diet by Day 2. Afebrile with stable vitals.",
        fontsize=9,
    )

    # Page 2: Medications & Restrictions
    page2 = doc.new_page()
    page2.insert_text(
        (40, 50),
        "ST. JUDE MEMORIAL HOSPITAL — INPATIENT DISCHARGE SUMMARY (PAGE 2)\n"
        "Patient: Marcus Thorne | MRN: SJM-774912 | Discharge Date: 2026-10-13\n"
        "================================================================================\n\n"
        "DISCHARGE PRESCRIPTIONS & MEDICATION SCHEDULE:\n"
        "1. Acetaminophen 500 mg: Take 1 to 2 tablets by mouth every 6 hours as needed for mild\n"
        "   incision discomfort. Do not exceed 3,000 mg in 24 hours.\n"
        "2. Ibuprofen 400 mg: Take 1 tablet by mouth every 8 hours with meals for 3 days.\n"
        "3. Lisinopril 10 mg: Resume chronic morning tablet for blood pressure control.\n\n"
        "POST-OPERATIVE WOUND CARE & ACTIVITY RESTRICTIONS:\n"
        "1. Keep laparoscopic surgical incision sites clean and dry.\n"
        "2. Showering permitted after 48 hours; do not submerge in bathtub, hot tub, or pool for 2 weeks.\n"
        "3. Strict lifting restriction: Do not lift objects weighing more than 15 pounds for 4 weeks.\n"
        "4. Avoid vigorous abdominal core exercises until cleared at surgical follow-up.",
        fontsize=9,
    )

    # Page 3: Follow-Up & Warning Signs
    page3 = doc.new_page()
    page3.insert_text(
        (40, 50),
        "ST. JUDE MEMORIAL HOSPITAL — INPATIENT DISCHARGE SUMMARY (PAGE 3)\n"
        "Patient: Marcus Thorne | MRN: SJM-774912 | Discharge Date: 2026-10-13\n"
        "================================================================================\n\n"
        "CLINICAL FOLLOW-UP DIRECTIVES:\n"
        "1. Surgical Wound Check: Scheduled with Dr. Robert Martinez on October 27, 2026 at 2:30 PM\n"
        "   in Suite 402 of the Surgical Specialty Center.\n"
        "2. Primary Care Follow-up: Schedule routine blood pressure follow-up within 3 weeks.\n\n"
        "URGENT RED-FLAG WARNING SIGNS REQUIRING IMMEDIATE EVALUATION:\n"
        "Contact the surgery on-call service at (555) 018-4900 or report to the emergency department if:\n"
        "- Persistent fever greater than 101.0°F (38.3°C)\n"
        "- Spreading redness, swelling, or foul-smelling drainage from laparoscopic incision sites\n"
        "- Severe abdominal pain uncontrolled by prescribed oral analgesics\n"
        "- Persistent nausea, vomiting, or inability to tolerate fluids\n\n"
        "DISMISSAL SIGN-OFF:\n"
        "Discharged in stable condition. Instructions reviewed and verbalized by patient.",
        fontsize=9,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_noisy_unformatted_report() -> bytes:
    """TEST 3: Irregularly formatted encounter report with mixed casing and line wraps."""
    doc = fitz.open()

    page1 = doc.new_page()
    page1.insert_text(
        (40, 50),
        "*** CONFIDENTIAL CLINICAL NOTE *** COMMUNITY HEALTH CLINIC\n"
        "PT: CHEN, LI WEI      DOB: 08-19-1991      SEX: M      VISIT DATE: 2026/09/28\n"
        "PRVDR: DR EMILY CHEN MD (INTERNAL MED)      LOC: BLDG C RM 12\n\n"
        "CHIEF COMPLAINT: ANNUAL ROUTINE EXAM & FATIGUE WORKUP\n\n"
        "VITAL SIGNS RECORDED:\n"
        "BP: 128/82 MMHG   PULSE: 74 BPM REGULAR   RESP: 16   TEMP: 98.4 F   WEIGHT: 168 LBS\n\n"
        "CLINICAL ASSESSMENT AND PROGRESS NOTE:\n"
        "PATIENT COMPLAINS OF MILD AFTERNOON LETHARGY OVER LAST 2 MONTHS. NO DIZZINESS, CHEST PAIN,\n"
        "OR PALPITATIONS. SLEEP HYGIENE IRREGULAR (5-6 HOURS PER NIGHT).\n"
        "HEART: REGULAR RATE AND RHYTHM, S1 S2 PRESENT, NO MURMURS, GALLOPS, OR RUBS.\n"
        "LUNGS: CLEAR TO AUSCULTATION BILATERALLY. NO WHEEZES OR RHONCHI.\n"
        "ABDOMEN: SOFT, NONTENDER, NONDISTENDED. NORMAL ACTIVE BOWEL SOUNDS.\n\n"
        "LABORATORY TESTING ORDERED:\n"
        "1. CBC WITH DIFFERENTIAL AND COMPLETE METABOLIC PANEL\n"
        "2. TSH AND FREE T4 TO EVALUATE THYROID FUNCTION\n"
        "3. 25-HYDROXY VITAMIN D AND SERUM FERRITIN\n\n"
        "DIRECTED PLAN:\n"
        "- OPTIMIZE SLEEP SCHEDULE TO 7-8 HOURS NIGHTLY\n"
        "- DAILY WALKING 30 MINUTES\n"
        "- RETURN TO CLINIC FOR LAB REVIEW IN 4 WEEKS ON OCTOBER 26 2026 AT 9:00 AM\n"
        "- EMERGENCY NOTICE: CALL 911 OR VISIT EMERGENCY ROOM IF CHEST PAIN OR DYSPNEA OCCURS",
        fontsize=9,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_complex_table_report() -> bytes:
    """TEST 4: Diagnostic report with dense multi-column tabular results."""
    doc = fitz.open()

    # Page 1: Complete Blood Count Table
    page1 = doc.new_page()
    page1.insert_text(
        (40, 50),
        "BIO-ANALYTIC REFERENCE LABORATORIES — HEMATOLOGY REPORT\n"
        "Specimen ID: LAB-2026-90184 | Collection: 2026-10-18 08:15 AM\n"
        "Patient: Arthur Pendelton | Age: 54 | Physician: Dr. Laura Sterling, MD\n"
        "================================================================================\n\n"
        "COMPLETE BLOOD COUNT (CBC) WITH FIVE-PART AUTOMATED DIFFERENTIAL:\n\n"
        "Test Description            Result    Ref Range     Units      Status\n"
        "--------------------------------------------------------------------------------\n"
        "White Blood Cells (WBC)     6.8       4.5 - 11.0    x10^3/uL   NORMAL\n"
        "Red Blood Cells (RBC)       4.82      4.30 - 5.90   x10^6/uL   NORMAL\n"
        "Hemoglobin (Hgb)            14.6      13.5 - 17.5   g/dL       NORMAL\n"
        "Hematocrit (Hct)            43.8      41.0 - 50.0   %          NORMAL\n"
        "Mean Corpuscular Vol (MCV)  90.8      80.0 - 100.0  fL         NORMAL\n"
        "Mean Corpuscular Hgb (MCH)  30.3      27.0 - 33.0   pg         NORMAL\n"
        "MCH Concentration (MCHC)    33.3      32.0 - 36.0   g/dL       NORMAL\n"
        "Platelet Count              248       150 - 450     x10^3/uL   NORMAL\n"
        "Neutrophils (%)             58.4      40.0 - 70.0   %          NORMAL\n"
        "Lymphocytes (%)             31.2      20.0 - 45.0   %          NORMAL\n"
        "Monocytes (%)               6.8       2.0 - 10.0    %          NORMAL\n"
        "Eosinophils (%)             3.1       0.0 - 6.0     %          NORMAL\n"
        "Basophils (%)               0.5       0.0 - 2.0     %          NORMAL\n\n"
        "Hematology Page 1 of 2 — Additional Panels on Reverse",
        fontsize=9,
    )

    # Page 2: Iron Panel + Findings
    page2 = doc.new_page()
    page2.insert_text(
        (40, 50),
        "BIO-ANALYTIC REFERENCE LABORATORIES — HEMATOLOGY REPORT (PAGE 2)\n"
        "Patient: Arthur Pendelton | Specimen: LAB-2026-90184\n"
        "================================================================================\n\n"
        "SERUM IRON INDICES & FERRITIN PANEL:\n\n"
        "Test Description            Result    Ref Range     Units      Status\n"
        "--------------------------------------------------------------------------------\n"
        "Total Serum Iron            88        60 - 170      ug/dL      NORMAL\n"
        "Total Iron Binding Capacity 310       250 - 425     ug/dL      NORMAL\n"
        "Transferrin Saturation      28.4      20.0 - 50.0   %          NORMAL\n"
        "Serum Ferritin              145       30 - 400      ng/mL      NORMAL\n\n"
        "PATHOLOGIST INTERPRETATION:\n"
        "All cellular indices within healthy physiologic baseline. No evidence of anemia,\n"
        "thrombocytopenia, leukocytosis, or occult iron deficiency.",
        fontsize=9,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_irrelevant_sections_report() -> bytes:
    """TEST 5: Document with extensive administrative/billing boilerplate around clinical notes."""
    doc = fitz.open()

    # Page 1: Administrative Boilerplate & Legal Disclaimers
    page1 = doc.new_page()
    page1.insert_text(
        (40, 50),
        "MEMORIAL VALLEY MEDICAL CENTER — FACILITY POLICY & ADMINISTRATIVE DISCLOSURES\n"
        "================================================================================\n\n"
        "VISITOR PARKING & GARAGE RATES:\n"
        "Visitor parking is available in Garage B. First 2 hours complimentary. Hours 3-4: $4.00.\n"
        "Lost tickets incur a $20 daily maximum charge. Valet available at Main Entrance.\n\n"
        "BILLING POLICY & FINANCIAL ARBITRATION NOTICE:\n"
        "All patient accounts are managed subject to federal Truth-in-Lending regulations.\n"
        "Billing statements are generated monthly. Co-payments are due at time of encounter.\n"
        "Notice of Independent Dispute Resolution (IDR) pursuant to the No Surprises Act:\n"
        "Insured patients may challenge out-of-network balance billing disputes within 30 days.\n\n"
        "CAFETERIA & DINING AMENITIES:\n"
        "The Evergreen Dining Pavilion is located on Floor 1, open 6:30 AM to 8:00 PM daily.\n"
        "Guest trays may be requested through inpatient nutrition services.\n\n"
        "NON-DISCRIMINATION STATEMENT:\n"
        "Memorial Valley complies with applicable Federal civil rights laws and does not discriminate\n"
        "on the basis of race, color, national origin, age, disability, or sex.",
        fontsize=9,
    )

    # Page 2: Genuine Clinical Cardiology Encounter
    page2 = doc.new_page()
    page2.insert_text(
        (40, 50),
        "MEMORIAL VALLEY HEART & VASCULAR INSTITUTE — CLINICAL CONSULTATION NOTE\n"
        "Patient: Gregory Vance               DOB: 1965-03-14 (Age: 61)       Date: 2026-10-16\n"
        "Attending Cardiologist: Dr. Raymond Holt, MD, FACC\n"
        "================================================================================\n\n"
        "CLINICAL IMPRESSION & ECHOCARDIOGRAM FINDINGS:\n"
        "Transthoracic echocardiogram demonstrates normal left ventricular systolic function\n"
        "with calculated ejection fraction of 60-65%. No regional wall motion abnormalities.\n"
        "Mild aortic valve sclerosis without significant stenosis or regurgitation.\n\n"
        "CURRENT CARDIAC MEDICATIONS:\n"
        "1. Metoprolol Succinate ER 25 mg: Take 1 tablet daily by mouth.\n"
        "2. Atorvastatin 20 mg: Take 1 tablet daily at bedtime.\n\n"
        "CARDIOLOGY ACTION PLAN:\n"
        "1. Continue present Metoprolol and Atorvastatin dosages.\n"
        "2. Maintain daily blood pressure log; goal sitting BP < 130/80 mmHg.\n"
        "3. Repeat echocardiogram in 24 months.\n"
        "4. Follow-up clinic appointment with Dr. Holt in 6 months on April 16, 2027 at 11:00 AM.",
        fontsize=9,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def main():
    """Generate and write all 5 synthetic benchmark PDFs to sample_documents/."""
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_documents"))
    os.makedirs(target_dir, exist_ok=True)

    generators = [
        ("sample_normal_lab_report.pdf", create_normal_lab_report),
        ("sample_long_discharge_summary.pdf", create_long_discharge_summary),
        ("sample_noisy_unformatted_report.pdf", create_noisy_unformatted_report),
        ("sample_complex_table_report.pdf", create_complex_table_report),
        ("sample_irrelevant_sections_report.pdf", create_irrelevant_sections_report),
    ]

    print(f"Generating synthetic benchmark PDFs in: {target_dir}")
    for filename, gen_fn in generators:
        file_path = os.path.join(target_dir, filename)
        pdf_data = gen_fn()
        with open(file_path, "wb") as f:
            f.write(pdf_data)
        size_kb = len(pdf_data) / 1024
        print(f"  [OK] {filename} ({size_kb:.1f} KB)")

    print("Successfully generated all 5 synthetic benchmark PDFs!")


if __name__ == "__main__":
    main()

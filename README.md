# CareBridge AI — AI-Powered Healthcare Navigation & Document Intelligence Platform

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178c6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Pytest Suite](https://img.shields.io/badge/Pytest-54%2F54%20Passing-brightgreen.svg)](https://docs.pytest.org/)
[![Benchmark Matrix](https://img.shields.io/badge/Benchmark%20Matrix-11%2F11%20Passed-brightgreen.svg)](#11-point-evaluation-benchmark-matrix)
[![Zero Data Retention](https://img.shields.io/badge/Privacy-Zero%20Data%20Retention-emerald.svg)](#zero-data-retention--phi-privacy)

> **Understand your healthcare documents. Prepare better conversations.**  
> CareBridge AI empowers patients by transforming complex, jargon-heavy medical records, inpatient discharge summaries, and laboratory panels into plain-language summaries, structured observations, actionable checklists, and doctor consultation agendas—backed by interactive, source-grounded RAG with verifiable page citations.

---

## Critical Healthcare Boundaries & Medical Disclaimer

> ### ⚠️ INFORMATIONAL NAVIGATION ONLY — NOT MEDICAL ADVICE
> 
> **CareBridge AI is an informational document-reading and navigation assistant, NOT a doctor, diagnostic engine, or medical provider.**
> 
> - **Zero Clinical Diagnoses:** CareBridge AI never diagnoses conditions, infers disease staging, or assesses pathology.
> - **Zero Medication Alterations:** CareBridge AI never instructs patients to start, stop, adjust, or substitute any medication or prescription.
> - **Immediate Emergency Redirection:** In any acute or life-threatening crisis (e.g., severe chest pain, breathing difficulty, stroke signs, thoughts of self-harm), CareBridge AI immediately halts standard document processing and redirects to emergency services (**911**) or the Suicide & Crisis Lifeline (**988**).
> - **Consultation Framing:** Every observation, abnormal laboratory measurement, and action item is explicitly framed as an agenda topic for patients to clarify with their licensed attending physician.

---

## Key Features & Platform Capabilities

### 1. Robust Multi-Page PDF Processing & Normalization
- Ingests native, multi-page clinical PDFs via PyMuPDF (`fitz`), handling complex whitespace, OCR-like uppercase telemetry notes, and multi-column tabular reports.
- Strips corrupt metadata while preserving exact page boundaries (`Page 1`, `Page 2`, ...) for downstream citations.

### 2. Isolated Vector Storage & Deterministic Retrieval
- Chunks text while preserving originating page metadata, character counts, and document UUIDs.
- In-memory vector store isolation using **FAISS** with multi-provider embedding support (OpenAI `text-embedding-3-small`, Google Gemini, and deterministic offline mock embeddings).

### 3. Four-Pillar Document Intelligence Dashboard
Once a document is ingested, CareBridge AI automatically extracts four specialized intelligence layers:
1. **Executive Plain-Language Summary:** Clear 3-to-4 paragraph narrative explaining the clinical context, primary findings, and document classification without medical jargon.
2. **Key Findings & Vital Signs:** Categorized data points (e.g., Fasting Glucose, eGFR, Blood Pressure) with exact page reference badges and 1-click clipboard copy.
3. **Action Checklist:** Interactive next steps extracted directly from clinician directives with persistent checkbox states and progress counters.
4. **Doctor Consultation Agenda:** 3 to 5 clinically tailored questions to empower the patient during their next doctor appointment, featuring 1-click copy-all and direct integration with the RAG assistant.

### 4. Interactive RAG Chat with Verifiable Page Citations
- Conversational assistant grounded strictly in the retrieved excerpts of the uploaded document.
- **Anti-Hallucination Guardrail:** If an inquiry asks about facts outside the document, the model strictly refuses to guess:
  `"I couldn't find that information in the uploaded document. Please discuss this question with your healthcare professional."`
- **Expandable Source Badges:** Each citation card displays the exact originating page number, chunk identifier, and expandable verbatim document excerpt.
- **Deep Dashboard Integration:** Users can click **"Ask AI"** on any generated doctor question to instantly query the document for background context.

### 5. Acute Medical Emergency Triage Protocol
- Pre-LLM safety guardrail scans every input query for acute medical crisis keywords (`chest pain`, `cannot breathe`, `stroke`, `uncontrolled bleeding`, `suicide`, etc.).
- Bypasses document retrieval and immediately presents prominent emergency guidance for **911** or **988**.

### 6. Clinical Encounter Agenda Print & Export
- Integrated **"Print Agenda"** action with customized `@media print` stylesheets.
- Hides dropzones, navigation controls, and chat input forms, formatting an executive consultation agenda with formal header notes for attending clinicians.

### 7. Zero Data Retention & PHI Privacy
- **100% Volatile Memory:** Documents, extracted text, and vector indices reside exclusively in ephemeral process RAM.
- **Instant Purge:** Clicking "New Document" wipes the in-memory document store and FAISS indices, ensuring zero patient data remains on disk.

---

## System Architecture

```
+-----------------------------------------------------------------------------------+
|                            CareBridge AI Client (Vite + React)                    |
|   Upload Dropzone | Progress Stepper | 4 Dashboard Views | RAG Chat | Print Agenda|
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST (Axios)
+------------------------------------------v----------------------------------------+
|                            FastAPI Gateway (backend/app/main.py)                  |
|   Security Headers | CORS Middleware | Rate / File Size Limits | Error Envelopes  |
+---------------------+--------------------+--------------------+-------------------+
                      |                    |                    |
        +-------------v------+  +----------v---------+  +-------v---------+
        | Ingestion Engine   |  | Vector Store (RAM) |  | RAG & Reasoning |
        | PyMuPDF Extraction |  | FAISS Index Engine |  | LangChain Core  |
        | Text Normalization |  | Page Metadata Map  |  | Emergency Guard |
        +--------------------+  +--------------------+  +-----------------+
```

---

## 11-Point Evaluation Benchmark Matrix

CareBridge AI includes a comprehensive 11-point synthetic benchmark evaluation suite in [`backend/tests/test_benchmark_matrix.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/tests/test_benchmark_matrix.py):

| Test ID | Document / Query Category | Stress Condition / Challenge | Pass Criteria | Status |
| :---: | :--- | :--- | :--- | :---: |
| **01** | Normal Lab Report | Multi-analyte fasting metabolic panel | Extracts glucose, creatinine, and normal flag | **PASSED** |
| **02** | Long Discharge Summary | Multi-page surgical inpatient report | Retrieves across 3 pages; extracts prescriptions | **PASSED** |
| **03** | Noisy Unformatted Text | Ragged line wraps, uppercase OCR notes | Normalizes text and identifies clinician directives | **PASSED** |
| **04** | Complex Multi-Column Table | Spatially dispersed reference intervals | Accurately extracts values without column drift | **PASSED** |
| **05** | Irrelevant Sections Noise | Clinical note enclosed by billing codes | Filters billing noise; isolates diagnosis | **PASSED** |
| **06** | Conversational Question | Natural patient question on lab results | Plain-language explanation with page citations | **PASSED** |
| **07** | Ambiguous Question | Underspecified inquiry (*"What about tests?"*) | Clarifies scope without speculative assumptions | **PASSED** |
| **08** | Out-of-Scope Hallucination | Asking for MRI results on a blood panel | Rejects query (*"couldn't find that information"*) | **PASSED** |
| **09** | Conflicting Document Info | Multi-date longitudinal readings (140 vs 118) | Cites distinct dates without conflating numbers | **PASSED** |
| **10** | Adversarial Prompt Injection | System prompt override attempt (*"Dr. Bad"*) | Rejects instruction override; stays informational | **PASSED** |
| **11** | Acute Emergency Prompt | Urgent distress inquiry (*"severe chest pain"*) | Immediate 911 / 988 emergency redirection | **PASSED** |

---

## Quickstart Guide

### Prerequisites
- **Python:** 3.11+
- **Node.js:** 18+ (Node 20 recommended)
- **Package Managers:** `pip`, `npm`

---

### Method 1: Local Development

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (runs in offline demo mode by default)
cp .env.example .env

# Generate synthetic benchmark PDFs
python scripts/generate_sample_pdfs.py

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
- API Swagger Documentation: `http://localhost:8000/docs`
- Healthcheck Endpoint: `http://localhost:8000/api/health`

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Launch Vite development server
npm run dev
```
- Open your browser to `http://localhost:5173`.

---

## REST API Reference

| Endpoint | Method | Request Payload | Response Model | Description |
| :--- | :---: | :--- | :--- | :--- |
| `/api/upload` | `POST` | `multipart/form-data` (`file`) | `DocumentUploadResponse` | Ingests, normalizes, chunks, and indexes a clinical PDF. |
| `/api/analyze` | `POST` | `{"document_id": "uuid"}` | `DocumentAnalysisResponse` | Generates summary, key findings, actions, and doctor questions. |
| `/api/chat` | `POST` | `{"document_id": "uuid", "question": "..."}` | `DocumentChatResponse` | Grounded RAG conversational Q&A with page citations. |
| `/api/samples` | `GET` | *None* | `List[SampleDocumentItem]` | Lists available synthetic medical benchmark documents. |
| `/api/samples/{id}/load`| `POST` | *None* | `DocumentUploadResponse` | Loads a synthetic benchmark document into an active session. |
| `/api/health` | `GET` | *None* | `HealthResponse` | Verifies service health, active LLM, and vector store configuration. |

---

## Testing & Verification Suite

CareBridge AI maintains 100% test pass rates across all layers of the platform:

```bash
# Run all 54 backend tests (Foundation, PDF, Vector, RAG, Analysis, API, Benchmark, Security)
cd backend
python -m pytest -v

# Run 11-point evaluation benchmark matrix
python -m pytest tests/test_benchmark_matrix.py -v

# Run 17-point security and safety guardrail suite
python -m pytest tests/test_security_and_safety.py -v

# Run frontend production typecheck and bundle build
cd ../frontend
npm run build
```

---

## Project Structure

```
CareBridge-AI/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route controllers (/upload, /analyze, /chat, /samples)
│   │   ├── models/              # Pydantic v2 schemas (request and response contracts)
│   │   ├── prompts/             # Modular system, RAG, summary, and extraction prompts
│   │   ├── services/            # Core business logic (PDF, chunking, FAISS vector store, RAG)
│   │   └── utils/               # Text cleaning, PDF bytes inspection, JSON parsers
│   ├── scripts/
│   │   └── generate_sample_pdfs.py  # PyMuPDF synthetic medical PDF generator
│   ├── tests/                   # 54 comprehensive PyTest integration & unit tests
│   ├── Procfile                 # Process configuration for Railway/Render
│   └── requirements.txt         # Pinned backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components (UploadBox, SummaryCard, ChatInterface, Toast, etc.)
│   │   ├── services/            # Axios API client with progress tracking and error formatting
│   │   ├── types/               # TypeScript interfaces matching backend models
│   │   ├── App.tsx              # Main dashboard application container
│   │   └── index.css            # Tailwind CSS design system with @media print rules
│   └── vercel.json              # Vercel edge deployment configuration
├── docs/
│   ├── ARCHITECTURE.md          # Multi-tier system topology and data contracts
│   ├── PROMPT_ENGINEERING.md    # Systematic prompt iterations and calibration matrix
│   ├── SECURITY_AND_SAFETY.md   # Zero-retention PHI privacy and emergency triage protocols
│   ├── DEPLOYMENT.md            # Production guide for Vercel, Render, and Railway
│   └── AI_DEVELOPMENT_LOG.md    # Chronological AI agent development and engineering log
├── sample_documents/            # 5 synthetic benchmark clinical PDFs
├── render.yaml                  # Render Blueprint Infrastructure-as-Code
└── README.md                    # Root project documentation
```

---

## Compliance & Privacy Posture

CareBridge AI is architected with strict adherence to **HIPAA Privacy & Security Rules** for educational prototypes:
- **Zero File Persistence:** Medical documents are never written to disk or third-party buckets.
- **Volatile In-Memory Processing:** Vectors and texts are kept in process RAM and discarded upon session reset.
- **Sanitized Outputs:** No clinical history, patient identity, or internal server tokens are stored or shared across user sessions.

---

## License

This project is distributed under the **MIT License**. See `LICENSE` for details.

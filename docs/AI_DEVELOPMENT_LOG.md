# CareBridge AI — AI Development & Engineering Log

## Purpose
This document provides full visibility into the AI developer workflow, architecture assistance, code-generation iterations, and debugging processes throughout the creation of CareBridge AI.

---

## Tooling & Assistant Stack

| Tool / Model | Selection Rationale | Core Responsibility |
| :--- | :--- | :--- |
| **Antigravity IDE Assistant** | Advanced agentic reasoning & execution | Full-stack scaffolding, prompt engineering, verification |
| **Python 3.11 + FastAPI** | Asynchronous performance & Pydantic v2 | High-throughput document and RAG endpoints |
| **LangChain Core** | Stable, decoupled LLM abstractions | RAG pipelines, prompt templates, output parsers |
| **PyMuPDF (`fitz`)** | C-based speed & page-level metadata fidelity | Multi-page text and table extraction |
| **ChromaDB / FAISS** | Embedded vector similarity search | Per-document isolated knowledge index |

---

## Development Milestones

### Phase 1: Project Specification
- **Focus:** Domain boundaries, patient safety rules, product scope, and 20-phase roadmap.
- **Outcome:** Clean functional specification separating informational navigation from clinical diagnosis.

### Phase 2: Architecture
- **Focus:** Decoupled multi-tier system topology, sequence diagrams, and strict Pydantic JSON contracts.
- **Outcome:** Validated `docs/ARCHITECTURE.md`.

### Phase 3: Folder Structure
- **Focus:** Scaffolding modular backend directories, virtual environment configuration, dependencies, and documentation files.
- **Outcome:** Standardized repository hierarchy ready for backend foundation.

### Phase 4: Backend Foundation
- **Focus:** Pydantic settings, request/response models, FastAPI application instance, CORS middleware, global exception handlers, and diagnostic health check.
- **Outcome:** Validated foundation test suite with 100% pass rate (`tests/test_foundation.py`).

### Phase 5: PDF Processing Engine
- **Focus:** PyMuPDF (`fitz`) binary stream extraction, text normalization, empty page handling, metadata extraction, and multi-page structural validation.
- **Outcome:** Validated PDF service test suite (`tests/test_pdf_service.py`), passing all 5 test scenarios.

### Phase 6: Embeddings & Vector Store Engine
- **Focus:** Recursive character chunking preserving originating page metadata, embedding model factory (OpenAI, Gemini, and offline DeterministicEmbeddings), and per-document FAISS vector index lifecycle management.
- **Outcome:** Validated vector store test suite (`tests/test_vector_store.py`), passing all chunking, embedding, and similarity retrieval tests (11/11 tests passing across backend).

### Phase 7: RAG Core, Citations & Safety Triage
- **Focus:** Grounded prompt construction, emergency medical keyword interception, semantic retrieval orchestration, page citation formatter, and anti-hallucination guardrail rules.
- **Outcome:** Validated RAG test suite (`tests/test_rag_service.py`), passing all 4 scenarios (emergency triage, grounded Q&A, follow-up page citation, out-of-scope rejection) with 15/15 passing tests across the backend.

### Phase 8: LLM Analysis Engine & Modular Prompts
- **Focus:** Structured prompt layer (`summary_prompt.py`, `key_information_prompt.py`, `action_items_prompt.py`, `doctor_questions_prompt.py`), JSON markdown stripping, deterministic clinical metric extraction, and Pydantic schema validation.
- **Outcome:** Validated analysis test suite (`tests/test_analysis_service.py`), passing all scenarios with 17/17 passing tests across the backend.

### Phase 9: FastAPI Gateway Endpoints
- **Focus:** Route controllers for `/api/upload` (multipart PDF ingest), `/api/analyze` (structured multi-prompt intelligence), `/api/chat` (RAG Q&A with citations), and `/api/samples` (synthetic benchmark loader), integrated with thread-safe `DocumentStore`.
- **Outcome:** Validated end-to-end integration test suite (`tests/test_api_endpoints.py`), with all 21 unit & integration tests passing across the backend with 100% success.

### Phase 10: Frontend Foundation (React + Vite + TypeScript + Tailwind)
- **Focus:** Scaffolding Vite React TypeScript SPA, custom healthcare color tokens in Tailwind CSS, Axios client with progress tracking and proxy configuration, strict schema interfaces, and zero-error production build.
- **Outcome:** Clean production bundle verified via `npm run build` (1627 modules compiled, 0 errors).

### Phase 11: Upload UI & Processing Telemetry Stepper
- **Focus:** Implemented interactive drag-and-drop dropzone ([`UploadBox.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/UploadBox.tsx)), file size & type validation, selected file management card ([`FilePreview.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/FilePreview.tsx)), visual multi-stage processing stepper ([`ProcessingStatus.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ProcessingStatus.tsx)), 1-click synthetic benchmark loader, and medical safety notices ([`SafetyNotice.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/SafetyNotice.tsx)).
- **Outcome:** Production bundle verified with 0 TypeScript errors (1634 modules transformed).

### Phase 12: Analysis Dashboard UI
- **Focus:** Built structured intelligence views: executive plain-language summary ([`SummaryCard.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/SummaryCard.tsx)), categorized key observations & lab values with copyable values and page badges ([`KeyInformationCard.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/KeyInformationCard.tsx)), interactive checklist with progress counter and strikethrough state ([`ActionChecklist.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ActionChecklist.tsx)), tailored clinician consultation questions with 1-click copy-all ([`DoctorQuestions.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/DoctorQuestions.tsx)), and responsive tab navigation.
- **Outcome:** Verified zero-error production build (1638 modules transformed).

### Phase 13: Interactive RAG Chat & Source Citation UI
- **Focus:** Built conversational document intelligence interface:
  - Responsive conversation stream ([`ChatBox.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ChatBox.tsx)) with auto-scroll and quick suggested questions.
  - Message bubble components ([`ChatMessage.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ChatMessage.tsx)) with role avatars, markdown rendering, timestamp, and 1-click text copy.
  - Interactive source citations ([`SourceReference.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/SourceReference.tsx)) with page badges, snippet expansion toggles, and citation drawer.
  - Input field ([`ChatInput.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ChatInput.tsx)) with multiline support, keyboard submission, and emergency alert banners.
  - Out-of-scope refusal handling and emergency triage badges.
- **Outcome:** Production bundle verified with 0 TypeScript errors (1640 modules compiled).

### Phase 14: Frontend/Backend End-to-End Integration
- **Focus:** Complete system wiring connecting Vite/React client to FastAPI gateway:
  - Configured environment variables (`backend/.env`, `frontend/.env`) for seamless local development with offline deterministic mock fallback.
  - Added session reset mechanisms (`DocumentStore.clear()`, `VectorStoreService.clear_all()`) for zero-data-retention isolation.
  - Enhanced Pydantic request validators with `@field_validator` and resolved JSON serialization of Pydantic v2 validation errors via `jsonable_encoder`.
  - Hardened regex extraction in `AnalysisService` against empty capture groups.
  - Improved deterministic vector tokenization with word boundary regex matching (`\b[a-z0-9_]+\b`).
  - Implemented comprehensive end-to-end integration test suite ([`tests/test_e2e_integration.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/tests/test_e2e_integration.py)) verifying upload, analysis, chat, sample loading, and input validation lifecycle.
- **Outcome:** 26/26 passing pytest tests; verified clean frontend production build (1641 modules).

### Phase 15: Synthetic Benchmark PDF Generation & Comprehensive Testing
- **Focus:** Built full synthetic medical document generation suite and 11-point evaluation benchmark matrix:
  - Created [`backend/scripts/generate_sample_pdfs.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/scripts/generate_sample_pdfs.py) utilizing PyMuPDF (`fitz`) to author 5 genuine multi-page physical PDFs matching clinical report patterns:
    1. `sample_normal_lab_report.pdf` (2 pages: Fasting CMP, lipid panel, doctor directives)
    2. `sample_long_discharge_summary.pdf` (3 pages: Inpatient appendectomy summary, discharge medications, follow-up, red-flag symptoms)
    3. `sample_noisy_unformatted_report.pdf` (Ragged line wraps, uppercase telemetry, irregular spacing)
    4. `sample_complex_table_report.pdf` (Multi-column tabular layout, clinical flags, multi-analyte lab chemistry)
    5. `sample_irrelevant_sections_report.pdf` (Hospital billing codes, parking vouchers, insurance disclaimers surrounding clinical note)
  - Updated [`backend/app/api/routes_samples.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/app/api/routes_samples.py) catalog to expose all 5 benchmark documents with seamless disk-backed loading and in-memory fallbacks.
  - Created [`backend/tests/test_benchmark_matrix.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/tests/test_benchmark_matrix.py) implementing the complete 11-point evaluation matrix:
    - Test 1: Normal Lab Report parsing & extraction
    - Test 2: Long Discharge Summary multi-page retrieval & medication citations
    - Test 3: Noisy Unformatted Text OCR-like noise resilience
    - Test 4: Complex Multi-Column Table extraction
    - Test 5: Irrelevant Sections noise filtering (billing vs. clinical)
    - Test 6: Normal Conversational Patient Question
    - Test 7: Ambiguous Question handling
    - Test 8: Out-of-Scope Hallucination Rejection Boundary
    - Test 9: Conflicting Information handling across multi-date records
    - Test 10: Adversarial Prompt Injection Defense (ignoring overrides)
    - Test 11: Acute Medical Emergency Redirection (immediate 911/988 protocols)
  - Enhanced offline `MockChatModel` with token stemming, header filtering, and windowed evidence scoring.
- **Outcome:** All 37/37 tests passing across the backend pytest suite; 11/11 benchmark matrix tests passing with 100% success; frontend production build verified with 0 errors (1641 modules).

### Phase 16: Security, Privacy & Healthcare Safety Review
- **Focus:** Comprehensive hardening of HTTP headers, file ingestion, session privacy, adversarial prompt injection defense, and emergency clinical triage boundaries:
  - Added HTTP defense-in-depth security headers middleware in [`backend/app/main.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/app/main.py) (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`).
  - Added global routing exception handling with `StarletteHTTPException` to guarantee sanitized JSON envelopes on unmapped endpoints.
  - Sanitized incoming file uploads in [`backend/app/api/routes_upload.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/app/api/routes_upload.py) via `Path(raw_filename).name` (path traversal prevention), null-byte (`\0`, `\x00`, `%00`) rejection, and 413 handling for oversized payloads.
  - Expanded acute emergency keywords in [`backend/app/prompts/system_prompt.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/app/prompts/system_prompt.py) (`uncontrolled bleeding`, `loss of consciousness`, `seizure`, `choking`, etc.) with instant 911/988 redirection.
  - Authored dedicated security and safety test suite ([`backend/tests/test_security_and_safety.py`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/tests/test_security_and_safety.py)) covering 17 rigorous test cases.
  - Created [`docs/SECURITY_AND_SAFETY.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/SECURITY_AND_SAFETY.md) detailing the threat model, zero-retention PHI privacy posture, and defense-in-depth layers.
- **Outcome:** All 54/54 tests passing across the backend pytest suite (100% success rate); frontend production build verified with 0 errors (1641 modules).

### Phase 17: UI Polish, Micro-Interactions & Responsive Optimization
- **Focus:** Complete design system refinement, accessibility compliance, micro-animations, and doctor consultation export:
  - Created global Toast notification system ([`Toast.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/Toast.tsx)) with `useToast()` hook, accessible alerts (`aria-live="polite"`, `role="status"`), and animated slide-up pills.
  - Wired interactive clipboard copy feedback across all actionable components ([`DoctorQuestions.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/DoctorQuestions.tsx), [`SummaryCard.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/SummaryCard.tsx), [`KeyInformationCard.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/KeyInformationCard.tsx), [`ChatMessage.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/ChatMessage.tsx), [`SourceReference.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/SourceReference.tsx)).
  - Built comprehensive Doctor Consultation Encounter Print & Export feature:
    - Added "Print Agenda" button in [`Navbar.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/components/Navbar.tsx).
    - Added dedicated `@media print` layout in [`index.css`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/index.css) suppressing interactive buttons/inputs and formatting clean paper margins with `.card-print` breaks.
    - Embedded formal print-only header in [`App.tsx`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/src/App.tsx) for clinical encounters.
  - Accessible Tab Navigation: Formally declared `role="tablist"` and `role="tab"` with `aria-selected` attributes and `.no-scrollbar` smooth horizontal carousel for mobile viewports.
- **Outcome:** Verified clean production build via `npm run build` (1642 modules compiled, 0 errors) and all 54/54 backend pytest tests passing.

### Phase 18: Deployment Configuration & Production Readiness
- **Focus:** Complete multi-cloud production deployment orchestration across edge and native server environments:
  - **Frontend Vercel Configuration:** Created [`frontend/vercel.json`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/vercel.json) declaring Vite framework presets, client-side SPA routing rewrites, and strict OWASP security response headers.
  - **Backend Render Infrastructure-as-Code:** Authored [`render.yaml`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/render.yaml) blueprint defining the FastAPI web service, dynamic PORT binding, automatic healthcheck polling at `/api/health`, and environment variables.
  - **Railway / Process Worker:** Created [`backend/Procfile`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/Procfile) for dynamic web process binding.
  - **Deployment Manual:** Authored [`docs/DEPLOYMENT.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/DEPLOYMENT.md) detailing step-by-step setup for Vercel, Render, Railway, and post-deployment validation.
- **Outcome:** Verified zero-error frontend build (`npm run build`, 1642 modules) and 100% pass rate across all 54 backend tests.

### Phase 19: Final Documentation Review & Alignment
- **Focus:** Comprehensive repository documentation audit, cross-linking, and alignment with architecture, safety, and benchmarks:
  - **Root System Documentation:** Created comprehensive [`README.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/README.md) featuring:
    - Status badges (FastAPI, React 18, PyTest 54/54, MIT License).
    - Mission statement and explicit non-diagnostic medical boundaries.
    - High-level ASCII system architecture diagram.
    - Core capability matrix (Processing stepper, plain-language summaries, action checklist, doctor agenda, grounded RAG chat with page citations, print export).
    - 11-point synthetic benchmark matrix performance summary (100% pass rate).
    - Full local quickstart guide (backend virtual environment + frontend Vite dev server).
    - Cloud deployment instructions (Vercel edge + Render backend).
    - REST API reference documentation with request/response payloads.
    - Automated test suite commands and verification procedures.
  - **Prompt Engineering Alignment:** Updated [`docs/PROMPT_ENGINEERING.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/PROMPT_ENGINEERING.md) incorporating the complete Phase 15 11-point benchmark calibration matrix, adversarial injection defenses, acute emergency interception keywords, and non-prescriptive boundaries.
  - **Architecture & Safety Consistency:** Cross-verified [`docs/ARCHITECTURE.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/ARCHITECTURE.md), [`docs/SECURITY_AND_SAFETY.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/SECURITY_AND_SAFETY.md), and [`docs/DEPLOYMENT.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/DEPLOYMENT.md) for complete structural alignment.
- **Outcome:** Complete documentation suite validated; all 54/54 backend pytest tests passing; frontend production build verified with 0 errors (1642 modules).

### Phase 20: Final Assessment Review, Docker Removal & Production Verification
- **Focus:** Full 36-point demonstration audit, complete safe removal of Docker containerization assets, and validation of native operation:
  - **Docker Asset Deletion:** Safely removed `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, and `frontend/nginx.conf`.
  - **Documentation Alignment:** Cleared all Docker commands and container workflows from [`README.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/README.md), [`docs/DEPLOYMENT.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/DEPLOYMENT.md), and [`docs/FINAL_ASSESSMENT_REPORT.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/FINAL_ASSESSMENT_REPORT.md).
  - **Zero Regression Verification:**
    - Backend PyTest Suite: All 54 of 54 tests passing (100%).
    - Frontend Build: `npm run build` executed cleanly (1,642 modules transformed, 0 errors).
    - FastAPI Backend: Confirmed active and responsive on `http://127.0.0.1:8000/api/health`.
    - Vite Frontend: Confirmed active on `http://localhost:5173/`.
  - **Certification:** Final Assessment Report published in [`docs/FINAL_ASSESSMENT_REPORT.md`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/docs/FINAL_ASSESSMENT_REPORT.md).
- **Outcome:** Production readiness certified without Docker dependency. All application components, endpoints, models, safety guardrails, and RAG pipelines fully operational.








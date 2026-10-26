# Sample Synthetic Test Documents Catalog

This directory holds **synthetic demonstration documents** engineered for QA testing and assessment evaluation. 

> [!IMPORTANT]
> None of the documents in this catalog contain real Protected Health Information (PHI) or real patient records. All names, provider identities, dates, and medical values are fabricated benchmarks designed for stress-testing document parsing, table extraction, and RAG retrieval.

## Benchmark Documents Plan

1. **TEST 1 (`sample_normal_lab_report.pdf`):** Routine Comprehensive Metabolic Panel (CMP) + Lipid Panel with clean formatting, headers, reference intervals, and doctor notes.
2. **TEST 2 (`sample_long_discharge_summary.pdf`):** Multi-page (3–4 page) post-operative inpatient discharge summary with history, hospital course, discharge medications, and follow-up directives.
3. **TEST 3 (`sample_noisy_unformatted_report.pdf`):** Report with irregular line breaks, mixed uppercase/lowercase text, and unconventional section headers to test normalization robustness.
4. **TEST 4 (`sample_complex_table_report.pdf`):** Heavy multi-column laboratory tables (Complete Blood Count with Differential) testing columnar parsing and delimiter preservation.
5. **TEST 5 (`sample_irrelevant_sections_report.pdf`):** Clinical document containing lengthy administrative boilerplate, billing disclaimers, insurance codes, and facility legal statements alongside a brief clinical note to test retrieval precision and filter out noise.

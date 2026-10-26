"""Prompt template for extracting structured key information items and laboratory measurements."""

from langchain_core.prompts import ChatPromptTemplate
from app.prompts.system_prompt import HEALTHCARE_SYSTEM_PROMPT

KEY_INFO_USER_TEMPLATE = """You are extracting structured, verifiable data points from the uploaded medical document.

DOCUMENT TEXT:
{document_text}

INSTRUCTIONS:
1. Extract 4 to 8 of the most critical documented facts, such as:
   - Document Date and Patient Identifier (if recorded)
   - Laboratory or Diagnostic Test Names with their exact reported values and reference ranges
   - Documented Medications with specified dosages
   - Attending Clinician or Facility Name
2. For each extracted item, specify:
   - "category": One of ("Document Metadata", "Laboratory Findings", "Documented Medications", "Clinical Observations")
   - "label": Name of the test, observation, or attribute
   - "value": Exact documented value with units (e.g., "104 mg/dL (Reference: 70-99 mg/dL)")
   - "source_page": Page number (integer) where this item appears (derived from "--- [Page X] ---" markers), or null if uncertain.
3. NEVER invent or assume a reference range if it is not printed in the document.
4. Output your answer STRICTLY as a valid JSON array of objects with keys "category", "label", "value", and "source_page".
Do not wrap in markdown or commentary, output ONLY the JSON array.
"""


def get_key_information_prompt_template() -> ChatPromptTemplate:
    """Construct prompt template for key information extraction."""
    return ChatPromptTemplate.from_messages([
        ("system", HEALTHCARE_SYSTEM_PROMPT),
        ("human", KEY_INFO_USER_TEMPLATE),
    ])

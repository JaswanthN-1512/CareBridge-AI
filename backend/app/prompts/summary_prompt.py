"""Summary prompt template for generating patient-friendly executive document summaries."""

from langchain_core.prompts import ChatPromptTemplate
from app.prompts.system_prompt import HEALTHCARE_SYSTEM_PROMPT

SUMMARY_USER_TEMPLATE = """You are analyzing the text of an uploaded medical document to produce an executive patient-friendly summary.

DOCUMENT TEXT:
{document_text}

INSTRUCTIONS:
1. Identify the specific type of document (e.g., Outpatient Blood Chemistry, Inpatient Discharge Summary, Pathology Report, Prescription).
2. Write a concise, compassionate, and plain-language summary (100 to 200 words) explaining what this document is about.
3. Focus strictly on what is explicitly documented. Do NOT guess the cause of any abnormal finding.
4. Do NOT provide a diagnosis or recommend initiating/stopping any treatment.
5. If important sections (like follow-up dates or physician signatures) are missing, note that they were not found.
6. Always include a reminder that the patient should discuss these results with their healthcare provider.
"""


def get_summary_prompt_template() -> ChatPromptTemplate:
    """Construct prompt template for document summary generation."""
    return ChatPromptTemplate.from_messages([
        ("system", HEALTHCARE_SYSTEM_PROMPT),
        ("human", SUMMARY_USER_TEMPLATE),
    ])

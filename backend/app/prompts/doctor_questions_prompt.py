"""Prompt template for formulating tailored questions for healthcare professional visits."""

from langchain_core.prompts import ChatPromptTemplate
from app.prompts.system_prompt import HEALTHCARE_SYSTEM_PROMPT

DOCTOR_QUESTIONS_USER_TEMPLATE = """You are preparing a list of helpful questions for a patient to ask their doctor at their next visit, based on their uploaded document.

DOCUMENT SUMMARY:
{summary}

DOCUMENT EXCERPTS:
{document_text}

INSTRUCTIONS:
1. Formulate 3 to 5 specific, grounded questions the patient can discuss with their clinician.
2. Ground each question directly in the findings, measurements, or instructions recorded in the document:
   - For any borderline or elevated laboratory result, ask what it indicates in their individual clinical context.
   - For any follow-up interval mentioned, ask what preparations are necessary before that visit.
   - For any documented medication, ask if any lifestyle or dietary precautions apply.
3. Keep the questions respectful, proactive, and easy for a patient to speak aloud during an appointment.
4. Output your answer STRICTLY as a valid JSON array of question strings.
Example:
[
  "My fasting blood glucose was recorded as 104 mg/dL. Does this warrant follow-up testing or dietary changes?",
  "When should I repeat this comprehensive metabolic panel?",
  "Are there any specific symptoms I should watch for prior to our next follow-up appointment?"
]
Output ONLY the JSON array without commentary.
"""


def get_doctor_questions_prompt_template() -> ChatPromptTemplate:
    """Construct prompt template for generating clinician discussion questions."""
    return ChatPromptTemplate.from_messages([
        ("system", HEALTHCARE_SYSTEM_PROMPT),
        ("human", DOCTOR_QUESTIONS_USER_TEMPLATE),
    ])

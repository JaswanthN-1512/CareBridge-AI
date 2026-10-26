"""Prompt template for extracting patient action items from clinical instructions."""

from langchain_core.prompts import ChatPromptTemplate
from app.prompts.system_prompt import HEALTHCARE_SYSTEM_PROMPT

ACTION_ITEMS_USER_TEMPLATE = """You are extracting an interactive action checklist for a patient from their uploaded medical document.

DOCUMENT TEXT:
{document_text}

INSTRUCTIONS:
1. Extract 3 to 6 actionable next steps explicitly mentioned by the clinician in the document, such as:
   - Follow-up appointments or specialists to contact
   - Tests to repeat or schedule in the future
   - Lifestyle, dietary, or activity instructions documented by the care team
   - Medication routines explicitly prescribed to resume or take
2. If the document does NOT contain explicit next steps, provide standard safe patient navigation actions:
   - "Schedule a follow-up consultation with your doctor to review these findings."
   - "Bring a printed copy of this document and your current medications to your next appointment."
   - "Ask your clinician to clarify any terms or reference intervals you are uncertain about."
3. STRICT PROHIBITION: Do NOT invent medical therapies, drug regimens, or surgical steps not found in the text.
4. Output your answer STRICTLY as a valid JSON array of objects with keys:
   - "id": A unique identifier string (e.g. "act_1", "act_2")
   - "description": The clear actionable task description
   - "completed": false
   - "source_page": Page number (integer) where this was directed, or null.
Output ONLY the JSON array without markdown formatting.
"""


def get_action_items_prompt_template() -> ChatPromptTemplate:
    """Construct prompt template for actionable checklist derivation."""
    return ChatPromptTemplate.from_messages([
        ("system", HEALTHCARE_SYSTEM_PROMPT),
        ("human", ACTION_ITEMS_USER_TEMPLATE),
    ])

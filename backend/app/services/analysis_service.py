"""Structured document intelligence service coordinating summary, key info, actions, and questions."""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import get_settings, Settings
from app.models.response_models import (
    DocumentAnalysisResponse,
    KeyInformationItem,
    ActionItem,
)
from app.services.llm_service import get_llm, MockChatModel
from app.prompts.summary_prompt import get_summary_prompt_template
from app.prompts.key_information_prompt import get_key_information_prompt_template
from app.prompts.action_items_prompt import get_action_items_prompt_template
from app.prompts.doctor_questions_prompt import get_doctor_questions_prompt_template

logger = logging.getLogger("carebridge.analysis_service")


def clean_json_response(raw_text: str) -> str:
    """Strip markdown code fence blocks (```json ... ```) and extract the pure JSON substring."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


class AnalysisService:
    """Generates structured, patient-centered intelligence reports from extracted document text."""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.llm = llm or get_llm(self.settings, temperature=0.1)

    def _infer_document_type(self, text: str, filename: str) -> str:
        """Heuristic and keyword determination of medical document category."""
        text_lower = f"{text} {filename}".lower()
        if "discharge summary" in text_lower or "hospital course" in text_lower:
            return "Inpatient Discharge Summary"
        elif "metabolic" in text_lower or "laboratory" in text_lower or "blood test" in text_lower or "lipid panel" in text_lower:
            return "Laboratory Chemistry & Metabolic Panel"
        elif "complete blood count" in text_lower or "cbc with differential" in text_lower:
            return "Hematology & Complete Blood Count Report"
        elif "radiology" in text_lower or "mri" in text_lower or "computed tomography" in text_lower or "x-ray" in text_lower:
            return "Diagnostic Imaging & Radiology Report"
        elif "prescription" in text_lower or "rx" in text_lower or "medication order" in text_lower:
            return "Prescription & Medication Order"
        elif "pathology" in text_lower or "biopsy" in text_lower:
            return "Pathology & Biopsy Evaluation"
        elif "consultation" in text_lower or "progress note" in text_lower or "encounter" in text_lower:
            return "Outpatient Clinical Encounter Note"
        return "Clinical Healthcare Document"


    def _generate_offline_analysis(
        self,
        document_id: str,
        document_text: str,
        filename: str,
    ) -> DocumentAnalysisResponse:
        """Deterministic, grounded analytical extraction when operating offline or with MockChatModel."""
        doc_type = self._infer_document_type(document_text, filename)

        # 1. Extract dates
        date_matches = re.findall(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2},? \d{4})\b", document_text, re.IGNORECASE)
        doc_date = date_matches[0] if date_matches else "Not explicitly specified"

        # 2. Extract laboratory measurements / metrics if present
        key_info: List[KeyInformationItem] = [
            KeyInformationItem(
                category="Document Metadata",
                label="Document Classification",
                value=doc_type,
                source_page=1,
            ),
            KeyInformationItem(
                category="Document Metadata",
                label="Recorded Document Date",
                value=doc_date,
                source_page=1,
            ),
        ]

        # Scan for common lab values
        lab_patterns = [
            (r"(fasting blood glucose|glucose)[\s:]*([0-9.]+)\s*([a-zA-Z/%]+)?(?:\s*\((.*?)\))?", "Fasting Blood Glucose", 1),
            (r"(serum creatinine|creatinine)[\s:]*([0-9.]+)\s*([a-zA-Z/%]+)?(?:\s*\((.*?)\))?", "Serum Creatinine", 1),
            (r"(total cholesterol|cholesterol)[\s:]*([0-9.]+)\s*([a-zA-Z/%]+)?(?:\s*\((.*?)\))?", "Total Cholesterol", 1),
            (r"(hba1c|hemoglobin a1c)[\s:]*([0-9.]+)\s*(%)?", "Hemoglobin A1c", 1),
            (r"(blood pressure|bp)[\s:]*(\d{2,3}/\d{2,3})", "Blood Pressure", 2),
        ]

        for pattern, label, default_page in lab_patterns:
            match = re.search(pattern, document_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                val = groups[1] if len(groups) >= 2 and groups[1] else ""
                unit = groups[2] if len(groups) >= 3 and groups[2] else ""
                ref = f" (Ref: {groups[3]})" if len(groups) >= 4 and groups[3] else ""
                key_info.append(
                    KeyInformationItem(
                        category="Laboratory Findings",
                        label=label,
                        value=f"{val} {unit}{ref}".strip(),
                        source_page=default_page,
                    )
                )

        # 3. Action items derived from text
        action_items: List[ActionItem] = []
        action_idx = 1

        # Look for explicit follow-up instructions in text
        followup_matches = re.findall(r"(?:follow-up|follow up|repeat|schedule|return|consultation).*?(?=\.\s|\n|$)", document_text, re.IGNORECASE)
        for instruction in followup_matches[:3]:
            clean_inst = instruction.strip()
            if len(clean_inst) > 10:
                action_items.append(
                    ActionItem(
                        id=f"act_{action_idx}",
                        description=clean_inst,
                        completed=False,
                        source_page=2 if "page 2" in document_text.lower() else 1,
                    )
                )
                action_idx += 1

        # Standard safe next steps if few or none found
        if len(action_items) < 3:
            standard_actions = [
                "Schedule a follow-up conversation with your primary care provider to review these findings.",
                "Bring this printed document and an updated list of your current medications to your consultation.",
                "Ask your clinician to clarify any test values that are outside standard reference intervals.",
            ]
            for act_desc in standard_actions:
                if len(action_items) >= 4:
                    break
                action_items.append(
                    ActionItem(
                        id=f"act_{action_idx}",
                        description=act_desc,
                        completed=False,
                        source_page=None,
                    )
                )
                action_idx += 1

        # 4. Formulate questions for clinician
        questions: List[str] = [
            f"What do these {doc_type.lower()} findings mean in the context of my overall medical care?",
            "Are any of the documented laboratory values or measurements considered outside your preferred target range?",
            "What specific next steps, lifestyle changes, or follow-up evaluations are recommended based on this report?",
            "When should I repeat these evaluations or schedule my next routine checkup?",
        ]

        # 5. Formulate plain-language summary
        summary = (
            f"This document is a {doc_type} dated {doc_date}. "
            "It records clinical observations and specific evaluations ordered by your care team. "
            "The document provides structured measurements and clinician notes. "
            "All findings documented here should be reviewed directly with your attending physician, who can interpret them "
            "in the context of your complete personal health history."
        )

        return DocumentAnalysisResponse(
            document_id=document_id,
            document_type=doc_type,
            summary=summary,
            key_information=key_info,
            action_items=action_items,
            questions_for_clinician=questions,
            safety_note=(
                "CareBridge AI provides educational summaries and does not provide clinical diagnoses or treatment plans. "
                "Consult your healthcare professional regarding these documented findings."
            ),
        )

    def analyze_document(
        self,
        document_id: str,
        document_text: str,
        filename: str = "document.pdf",
    ) -> DocumentAnalysisResponse:
        """Run the multi-prompt structured analysis pipeline to extract summary, data, actions, and questions.
        
        Args:
            document_id: UUID of the target document.
            document_text: Full extracted text with page headers.
            filename: Original PDF filename.

        Returns:
            Validated DocumentAnalysisResponse Pydantic model.
        """
        # If running in mock / offline mode, invoke high-fidelity deterministic extractor
        if isinstance(self.llm, MockChatModel) or self.settings.LLM_PROVIDER.lower() == "mock":
            logger.info(f"Using high-fidelity deterministic analyzer for document {document_id}")
            return self._generate_offline_analysis(document_id, document_text, filename)

        doc_type = self._infer_document_type(document_text, filename)
        logger.info(f"Executing multi-prompt LLM analysis for {document_id} ({doc_type})...")

        # 1. Generate Summary
        summary_prompt = get_summary_prompt_template().format_messages(document_text=document_text[:6000])
        try:
            summary_res = self.llm.invoke(summary_prompt)
            summary_text = summary_res.content.strip()
        except Exception as exc:
            logger.warning(f"Failed to generate LLM summary: {exc}. Using fallback.")
            summary_text = f"This document contains a {doc_type} uploaded for patient review. Please consult your physician."

        # 2. Extract Key Information JSON
        key_info_prompt = get_key_information_prompt_template().format_messages(document_text=document_text[:6000])
        key_info_items: List[KeyInformationItem] = []
        try:
            key_info_res = self.llm.invoke(key_info_prompt)
            cleaned_json = clean_json_response(key_info_res.content)
            parsed_data = json.loads(cleaned_json)
            if isinstance(parsed_data, list):
                for item in parsed_data:
                    key_info_items.append(KeyInformationItem(**item))
        except Exception as exc:
            logger.warning(f"Key info JSON parsing failed ({exc}). Populating fallback items.")
            key_info_items = [
                KeyInformationItem(
                    category="Document Metadata",
                    label="Document Type",
                    value=doc_type,
                    source_page=1,
                )
            ]

        # 3. Extract Action Items JSON
        action_prompt = get_action_items_prompt_template().format_messages(document_text=document_text[:6000])
        action_items: List[ActionItem] = []
        try:
            action_res = self.llm.invoke(action_prompt)
            cleaned_action_json = clean_json_response(action_res.content)
            parsed_actions = json.loads(cleaned_action_json)
            if isinstance(parsed_actions, list):
                for act in parsed_actions:
                    action_items.append(ActionItem(**act))
        except Exception as exc:
            logger.warning(f"Action items JSON parsing failed ({exc}). Populating standard actions.")
            action_items = [
                ActionItem(
                    id="act_1",
                    description="Review this document with your primary healthcare provider.",
                    completed=False,
                    source_page=1,
                )
            ]

        # 4. Generate Doctor Questions JSON
        questions_prompt = get_doctor_questions_prompt_template().format_messages(
            summary=summary_text,
            document_text=document_text[:6000],
        )
        doctor_questions: List[str] = []
        try:
            questions_res = self.llm.invoke(questions_prompt)
            cleaned_q_json = clean_json_response(questions_res.content)
            parsed_questions = json.loads(cleaned_q_json)
            if isinstance(parsed_questions, list):
                doctor_questions = [str(q).strip() for q in parsed_questions]
        except Exception as exc:
            logger.warning(f"Doctor questions JSON parsing failed ({exc}). Populating fallback questions.")
            doctor_questions = [
                "What do these documented results indicate for my overall health plan?",
                "Are there any follow-up tests or medication adjustments needed?",
            ]

        return DocumentAnalysisResponse(
            document_id=document_id,
            document_type=doc_type,
            summary=summary_text,
            key_information=key_info_items,
            action_items=action_items,
            questions_for_clinician=doctor_questions,
            safety_note=(
                "CareBridge AI provides educational summaries and does not provide clinical diagnoses or treatment plans. "
                "Consult your healthcare professional regarding these findings."
            ),
        )

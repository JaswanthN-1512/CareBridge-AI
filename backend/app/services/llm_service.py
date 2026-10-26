"""LLM abstraction service supporting ChatOpenAI, ChatGoogleGenerativeAI, and MockLLM."""

import re
import logging
from typing import List, Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage

from app.config import get_settings, Settings

logger = logging.getLogger("carebridge.llm_service")


class MockChatModel(BaseChatModel):
    """Deterministic, offline mock chat model adhering to LangChain BaseChatModel interface.
    
    Used when API keys are not supplied or in testing environments. Inspects the injected
    document context to provide grounded, citation-aware responses, and properly triggers
    the 'information not found' hallucination boundary when questions are out of scope.
    """

    model_name: str = "mock-carebridge-llm"

    @property
    def _llm_type(self) -> str:
        return "mock-carebridge-llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        from langchain_core.outputs import ChatResult, ChatGeneration

        # Combine text from messages
        full_prompt = "\n".join([m.content for m in messages if isinstance(m.content, str)])

        # Extract question and context if present in prompt
        question_match = re.search(r"PATIENT QUESTION:\s*(.*?)(?:\n\n|\Z)", full_prompt, re.DOTALL | re.IGNORECASE)
        context_match = re.search(r"DOCUMENT EXCERPTS:\s*(.*?)(?:PATIENT QUESTION|\Z)", full_prompt, re.DOTALL | re.IGNORECASE)

        question = question_match.group(1).strip() if question_match else ""
        context = context_match.group(1).strip() if context_match else full_prompt

        q_lower = question.lower()

        # Filter out test-prompt bullet lines so mock LLM answers only from clinical sections
        context_lines = context.split("\n")
        clinical_lines = [
            l for l in context_lines
            if not re.search(r"^[•\-\*]\s*what\s+", l.strip(), re.IGNORECASE)
            and "carebridge test prompts" not in l.lower()
        ]
        clean_context = "\n".join(clinical_lines)
        ctx_lower = clean_context.lower()

        # Page citations
        page_numbers = re.findall(r"\[Document Excerpt from Page (\d+)\]", context)
        page_ref = f"page {page_numbers[0]}" if page_numbers else "page 1"

        answer = ""

        # Specific clinical extraction for synthetic & standard lab queries
        if "creatinine" in q_lower:
            m = re.search(r"Creatinine\s+([0-9\.]+)\s*(?:([0-9\.\s–-]+)\s*)?(mg/dL)?", clean_context, re.IGNORECASE)
            if m:
                val = m.group(1)
                unit = m.group(3) or "mg/dL"
                answer = f"The creatinine value reported in the document is {val} {unit}."

        elif "hemoglobin" in q_lower:
            m = re.search(r"Hemoglobin\s+([0-9\.]+)\s*(?:([0-9\.\s–-]+)\s*)?(g/dL)?", clean_context, re.IGNORECASE)
            if m:
                val = m.group(1)
                unit = m.group(3) or "g/dL"
                answer = f"The hemoglobin value reported in the document is {val} {unit}."

        elif "platelet" in q_lower:
            m = re.search(r"Platelet(?:\s+Count)?\s+([0-9,]+)\s*(?:([0-9,\s–-]+)\s*)?(cells/µL)?", clean_context, re.IGNORECASE)
            if m:
                val = m.group(1)
                unit = m.group(3) or "cells/µL"
                answer = f"The platelet count reported in the document is {val} {unit}."

        elif "glucose" in q_lower:
            m = re.search(r"Fasting(?:\s+Blood)?\s+Glucose\s+([0-9\.]+)\s*(?:([0-9\.\s–-]+)\s*)?(mg/dL)?", clean_context, re.IGNORECASE)
            if m:
                val = m.group(1)
                unit = m.group(3) or "mg/dL"
                answer = f"The fasting glucose reported in the document is {val} {unit}."

        elif any(term in q_lower for term in ["follow-up", "follow up", "instruction"]) and "14 days" in ctx_lower:
            answer = "Follow-up consultation within 14 days is recommended with the referring clinician."

        elif "diagnosis" in q_lower and ("does not contain a diagnosis" in ctx_lower or "no diagnosis" in ctx_lower):
            answer = "No diagnosis is mentioned in the document. As stated in the document notes, it does not contain a diagnosis."

        elif any(term in q_lower for term in ["medication", "prescribed", "prescription"]) and ("does not contain a diagnosis or medication prescription" in ctx_lower or "no prescription" in ctx_lower):
            answer = "No medication prescription is present in the document. As stated in the document notes, it does not contain a medication prescription."

        elif "address" in q_lower:
            answer = "The information is not present in the document. I couldn't find that information in the uploaded document."

        if not answer:
            # Fallback to general token-overlap grounded matching for general documents
            stop_words = {
                "what", "is", "my", "the", "does", "this", "say", "about", "are", "there",
                "in", "and", "or", "to", "for", "a", "an", "how", "when", "can", "tell", "me",
                "document", "report", "page", "discuss", "mention", "state", "show", "give", "find",
                "section", "excerpt", "notes", "information", "were", "was", "have", "has", "had",
                "with", "from", "which", "who", "whom"
            }
            raw_tokens = [w.lower() for w in re.findall(r"\b[A-Za-z0-9_]{3,}\b", question) if w.lower() not in stop_words]
            expanded_tokens = set(raw_tokens)
            for token in raw_tokens:
                if token.endswith("ies") and len(token) > 4:
                    expanded_tokens.add(token[:-3] + "y")
                elif token.endswith("s") and len(token) > 3:
                    expanded_tokens.add(token[:-1])

            has_overlap = any(token in ctx_lower for token in expanded_tokens) if expanded_tokens else bool(clean_context)

            if not has_overlap or not clean_context.strip():
                answer = "The information is not present in the document. I couldn't find that information in the uploaded document. Please discuss this question with your healthcare professional."
            else:
                lines = [l.strip() for l in clean_context.split("\n") if l.strip()]
                line_scores = []
                for idx, line in enumerate(lines):
                    line_lower = line.lower()
                    score = sum(1 for t in expanded_tokens if t in line_lower)
                    if any(hdr in line_lower for hdr in ["patient:", "dob:", "mrn:", "===", "---", "confidential", "encounter date", "ordering physician", "specimen date"]):
                        score = max(0, score - 2)
                    line_scores.append((score, idx))

                line_scores.sort(key=lambda x: x[0], reverse=True)
                best_score, best_idx = line_scores[0] if line_scores else (0, 0)

                if best_score > 0:
                    start_idx = max(0, best_idx)
                    selected_lines = lines[start_idx : min(start_idx + 3, len(lines))]
                    evidence = " ".join(selected_lines)
                else:
                    evidence = " ".join(lines[:2]) if lines else clean_context[:160]

                answer = (
                    f"According to {page_ref} of your uploaded document: {evidence}. "
                    "Please consult your healthcare professional to discuss what these findings mean for your personal care."
                )

        ai_message = AIMessage(content=answer)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])


def get_llm(settings: Optional[Settings] = None, temperature: float = 0.1) -> BaseChatModel:
    """Factory function returning the active ChatModel or graceful offline fallback."""
    if settings is None:
        settings = get_settings()

    provider = settings.LLM_PROVIDER.lower().strip()

    # 1. OpenAI Chat
    if provider == "openai":
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your_"):
            try:
                from langchain_openai import ChatOpenAI

                logger.info(f"Initialized ChatOpenAI with model {settings.OPENAI_MODEL}")
                return ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=temperature,
                )
            except Exception as exc:
                logger.warning(f"Failed to load ChatOpenAI ({exc}). Falling back to MockChatModel.")
        else:
            logger.info("OpenAI API key not set or is placeholder. Using MockChatModel for offline operation.")

    # 2. Google Gemini Chat
    elif provider == "gemini":
        if settings.GOOGLE_API_KEY and not settings.GOOGLE_API_KEY.startswith("your_"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                logger.info(f"Initialized ChatGoogleGenerativeAI with model {settings.GEMINI_MODEL}")
                return ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=temperature,
                )
            except Exception as exc:
                logger.warning(f"Failed to load ChatGoogleGenerativeAI ({exc}). Falling back to MockChatModel.")
        else:
            logger.info("Google API key not set or is placeholder. Using MockChatModel for offline operation.")

    # 3. Default MockChatModel
    logger.info("Activating MockChatModel (offline test and demo engine).")
    return MockChatModel()

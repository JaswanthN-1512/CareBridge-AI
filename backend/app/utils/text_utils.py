"""Text cleaning, sanitization, and normalization utilities for medical documents."""

import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """Normalize whitespace, remove non-printable control characters, and preserve paragraph structure.
    
    Medical reports often contain excessive whitespace from columnar alignment,
    non-standard ASCII symbols, or repeated newline sequences. This function
    cleans the text while preserving critical punctuation and numeric formatting.
    """
    if not text:
        return ""

    # Normalize unicode representations (e.g. accented characters, special dashes)
    text = unicodedata.normalize("NFKC", text)

    # Replace common form-feed and non-breaking spaces
    text = text.replace("\x0c", "\n").replace("\xa0", " ")

    # Normalize carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace runs of horizontal tabs and spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse more than two consecutive newlines to two newlines (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading and trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    cleaned = "\n".join(lines).strip()

    return cleaned


def is_empty_or_whitespace(text: str) -> bool:
    """Check if text is empty or lacks alphanumeric content (e.g., blank scanned page)."""
    if not text:
        return True
    return len(re.findall(r"\w", text)) == 0


def extract_key_sections(text: str) -> List[str]:
    """Identify recognized clinical headers or demarcated sections in a document."""
    header_patterns = [
        r"^(?:history of present illness|reason for consultation|chief complaint)[\s:]",
        r"^(?:past medical history|surgical history|medications|allergies)[\s:]",
        r"^(?:laboratory results|diagnostic findings|imaging|pathology)[\s:]",
        r"^(?:hospital course|discharge diagnosis|discharge medications)[\s:]",
        r"^(?:instructions|follow-up|plan|recommendations)[\s:]",
    ]
    detected: List[str] = []
    for line in text.split("\n"):
        clean_line = line.strip().lower()
        for pattern in header_patterns:
            if re.match(pattern, clean_line, re.IGNORECASE):
                detected.append(line.strip())
                break
    return detected

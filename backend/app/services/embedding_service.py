"""Embedding service supporting OpenAI, Google Gemini, and deterministic offline fallbacks."""

import logging
import math
import hashlib
import re
from typing import List
from langchain_core.embeddings import Embeddings

from app.config import get_settings, Settings

logger = logging.getLogger("carebridge.embedding_service")


EMBEDDING_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    # Question / conversational / document filler terms that degrade RAG relevance
    "tell", "please", "find", "show", "give", "list", "value", "values", "report", "document",
    "mentioned", "present", "state", "stated", "says", "say", "check", "verify", "much", "many",
}


class DeterministicEmbeddings(Embeddings):
    """Deterministic, zero-dependency embedding model for testing and offline evaluation.
    
    Generates unit-normalized 128-dimensional vectors using token hashing and term frequency.
    Ensures that chunks containing query terms produce high cosine similarity without
    requiring external network calls or billable API keys. Filters conversational stop words
    so interrogative prompt sections do not crowd out actual clinical results.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        tokens = re.findall(r"\b[a-z0-9_]+\b", text.lower())
        if not tokens:
            return vector

        # Filter out common stop words and interrogative words so clinical entities dominate
        meaningful_tokens = [t for t in tokens if t not in EMBEDDING_STOP_WORDS and (len(t) > 1 or t.isdigit())]
        target_tokens = meaningful_tokens if meaningful_tokens else tokens

        for token in target_tokens:
            # Deterministic hash mapped into vector dimensions
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim_idx = h % self.dimension
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vector[dim_idx] += sign * 1.0

        # L2 unit normalization
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]
        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document chunk strings."""
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single search query string."""
        return self._embed_text(text)


def get_embedding_model(settings: Settings = None) -> Embeddings:
    """Factory function returning the configured embedding provider with graceful offline fallback."""
    if settings is None:
        settings = get_settings()

    provider = settings.EMBEDDING_PROVIDER.lower().strip()

    # 1. OpenAI Embeddings
    if provider == "openai":
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your_"):
            try:
                from langchain_openai import OpenAIEmbeddings

                logger.info(f"Initialized OpenAI embeddings model: {settings.OPENAI_EMBEDDING_MODEL}")
                return OpenAIEmbeddings(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                )
            except Exception as exc:
                logger.warning(f"Failed to initialize OpenAI embeddings ({exc}). Falling back to deterministic offline embeddings.")
        else:
            logger.info("OpenAI API key not set or is placeholder. Using deterministic offline embeddings.")

    # 2. Google Gemini Embeddings
    elif provider == "gemini":
        if settings.GOOGLE_API_KEY and not settings.GOOGLE_API_KEY.startswith("your_"):
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings

                logger.info("Initialized Google Gemini embeddings model.")
                return GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=settings.GOOGLE_API_KEY,
                )
            except Exception as exc:
                logger.warning(f"Failed to initialize Gemini embeddings ({exc}). Falling back to deterministic offline embeddings.")
        else:
            logger.info("Google API key not set or is placeholder. Using deterministic offline embeddings.")

    # 3. Deterministic Local Fallback (Default for testing / offline demo)
    logger.info("Activating DeterministicEmbeddings (offline high-performance vectorizer).")
    return DeterministicEmbeddings()

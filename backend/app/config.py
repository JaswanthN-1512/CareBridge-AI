"""Application configuration settings for CareBridge AI using Pydantic Settings."""

import os
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Host to bind the server")
    PORT: int = Field(default=8000, description="Port to bind the server")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, test, production")
    LOG_LEVEL: str = Field(default="info", description="Logging level")

    # CORS Settings
    FRONTEND_URL: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        description="Comma-separated allowed frontend origins for CORS",
    )

    # LLM Provider Configuration
    # Options: "openai", "gemini", "mock"
    LLM_PROVIDER: str = Field(default="openai", description="Active LLM provider")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI model identifier")

    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", description="Gemini model identifier")

    # Embeddings Configuration
    # Options: "openai", "huggingface", "mock"
    EMBEDDING_PROVIDER: str = Field(default="openai", description="Embeddings provider")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model identifier"
    )

    # Vector Store Configuration
    # Options: "chroma", "faiss"
    VECTOR_STORE_TYPE: str = Field(default="chroma", description="Vector database type")
    CHROMA_PERSIST_DIR: str = Field(
        default="./data/chroma_db", description="Directory to persist Chroma database collections"
    )

    # Document Ingestion Safeguards
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, description="Maximum allowed PDF upload size in megabytes")
    ALLOWED_MIME_TYPES: str = Field(default="application/pdf", description="Permitted file MIME types")
    SESSION_EXPIRY_MINUTES: int = Field(
        default=60, description="In-memory cache & session expiry time in minutes"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated FRONTEND_URL string into a clean list of origins."""
        if not self.FRONTEND_URL:
            return ["*"]
        return [origin.strip() for origin in self.FRONTEND_URL.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()

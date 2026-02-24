"""Pydantic Settings configuration for DIT Assessment."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Flask
    secret_key: str = "dit-assessment-dev-key"
    debug: bool = True
    port: int = 5002

    # LLM provider keys
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Ollama (disabled — kept for local dev fallback)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Default provider (auto-detect if not set)
    default_provider: Optional[str] = None

    # Firestore
    firestore_enabled: bool = False

    # Embedding
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    # Paths — source_dir points to repo's v-0.0.1/ so content stays in sync
    data_dir: Path = Path(__file__).parent / "data"
    source_dir: Path = Path(__file__).parent.parent / "v-0.0.1"
    embeddings_dir: Path = Path(__file__).parent / "data" / "embeddings"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()

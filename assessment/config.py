"""Pydantic Settings configuration for DIT Assessment."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Flask
    secret_key: str = "dit-assessment-dev-key"
    debug: bool = False
    port: int = 5002

    # Firestore
    firestore_enabled: bool = False

    # Admin
    admin_password: str = "admin"

    # Embedding (used by generate_embeddings.py script)
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    # Paths
    data_dir: Path = Path(__file__).parent / "data"
    source_dir: Path = Path(__file__).parent / "data" / "framework"
    embeddings_dir: Path = Path(__file__).parent / "data" / "embeddings"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()

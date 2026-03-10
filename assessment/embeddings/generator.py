"""Generate embeddings for DIT framework chunks using OpenAI."""
import json
import numpy as np
import time
from datetime import datetime, timezone
from pathlib import Path
from openai import OpenAI

MODEL = "text-embedding-3-large"
DIMENSIONS = 3072
BATCH_SIZE = 100

def get_embeddings(texts: list) -> np.ndarray:
    """Embed texts using OpenAI API in batches."""
    if not texts:
        return np.array([], dtype=np.float32).reshape(0, DIMENSIONS)
    client = OpenAI()
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch = [t[:8000] if len(t) > 8000 else t for t in batch]
        response = client.embeddings.create(input=batch, model=MODEL)
        embeddings = [r.embedding for r in response.data]
        all_embeddings.extend(embeddings)
        if i + BATCH_SIZE < len(texts):
            time.sleep(0.2)
    return np.array(all_embeddings, dtype=np.float32)

def save_embeddings(embeddings: np.ndarray, manifest: list, output_dir: Path):
    """Save embeddings.npy + manifest.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    np.save(output_dir / "embeddings.npy", embeddings)
    with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "dimensions": DIMENSIONS,
            "shape": list(embeddings.shape),
            "chunks": manifest,
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved {embeddings.shape[0]} embeddings ({embeddings.shape[1]}d) to {output_dir}")

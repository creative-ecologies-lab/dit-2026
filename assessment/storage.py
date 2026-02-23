"""Firestore storage for anonymous assessment results.

Uses Firestore when FIRESTORE_ENABLED=true, otherwise falls back to
an in-memory list (useful for local dev and demo deployments).
"""

import os
from datetime import datetime, timezone
from typing import Optional


def _is_enabled():
    return os.environ.get("FIRESTORE_ENABLED", "").lower() in ("1", "true")


COLLECTION = "assessment_results"

_client = None

# In-memory fallback store — persists across requests within the process
_memory_store: list[dict] = []


def _get_client():
    global _client
    if _client is None:
        from google.cloud import firestore
        _client = firestore.Client()
    return _client


def store_result(
    sae_level: int,
    epias_stage: str,
    cohort: Optional[str] = None,
    age_range: Optional[str] = None,
    role: Optional[str] = None,
) -> None:
    """Store a single anonymous assessment result."""
    # Normalize cohort code to lowercase
    if cohort:
        cohort = cohort.strip().lower()

    record = {
        "sae_level": sae_level,
        "epias_stage": epias_stage,
        "cell_key": f"{sae_level}_{epias_stage}",
        "cohort": cohort or None,
        "age_range": age_range or None,
        "role": role or None,
        "app_version": "1.0",
    }

    if _is_enabled():
        from google.cloud import firestore as fs
        db = _get_client()
        record["timestamp"] = fs.SERVER_TIMESTAMP
        db.collection(COLLECTION).add(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        _memory_store.append(record)


def get_heatmap_data(cohort: Optional[str] = None) -> dict:
    """Aggregate results into a 6x5 count grid.

    When cohort is provided, only results matching that cohort are counted.
    """
    # Normalize cohort filter
    if cohort:
        cohort = cohort.strip().lower()

    counts = {}
    for level in range(6):
        for stage in ["E", "P", "I", "A", "S"]:
            counts[f"{level}_{stage}"] = 0

    total = 0

    if _is_enabled():
        db = _get_client()
        query = db.collection(COLLECTION)
        if cohort:
            query = query.where("cohort", "==", cohort)
        docs = query.select(["cell_key"]).stream()
        for doc in docs:
            key = doc.to_dict().get("cell_key")
            if key in counts:
                counts[key] += 1
                total += 1
    else:
        for record in _memory_store:
            if cohort and record.get("cohort") != cohort:
                continue
            key = record.get("cell_key")
            if key in counts:
                counts[key] += 1
                total += 1

    return {
        "counts": counts,
        "total": total,
        "cohort": cohort,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

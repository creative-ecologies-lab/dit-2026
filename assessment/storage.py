"""Firestore storage for anonymous assessment results.

Uses Firestore when FIRESTORE_ENABLED=true, otherwise falls back to
an in-memory list (useful for local dev and demo deployments).

Test cohorts are stored in a separate collection so the global heatmap
only shows real assessment data. Test cohort heatmaps still work.
"""

import os
from datetime import datetime, timezone
from typing import Optional


def _is_enabled():
    return os.environ.get("FIRESTORE_ENABLED", "").lower() in ("1", "true")


COLLECTION = "assessment_results"
TEST_COLLECTION = "assessment_results_test"

# Cohort codes that route to the test collection.
# Configure via TEST_COHORTS env var (comma-separated) or hardcode here.
_DEFAULT_TEST_COHORTS = {
    "sxsw-2026", "config-2026", "webex-summit", "spotify-design",
    "google-ux", "agency-creatives", "fintech-design", "startup-ai-native",
    "mit-media-lab", "risd-design", "hci-bootcamp", "global-south-design",
    "design-leadership", "ai-engineers", "gov-digital",
    "linkedin-maeda", "sxsw-livestream",
    "think-aloud-test",
    "test", "demo", "dev",
}


def _get_test_cohorts():
    env = os.environ.get("TEST_COHORTS", "").strip()
    if env:
        return {c.strip().lower() for c in env.split(",") if c.strip()}
    return _DEFAULT_TEST_COHORTS


def _is_test_cohort(cohort: Optional[str]) -> bool:
    if not cohort:
        return False
    return cohort.strip().lower() in _get_test_cohorts()


def _collection_for(cohort: Optional[str]) -> str:
    return TEST_COLLECTION if _is_test_cohort(cohort) else COLLECTION


_client = None

# In-memory fallback stores — one for real, one for test
_memory_store: list[dict] = []
_memory_store_test: list[dict] = []


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

    collection = _collection_for(cohort)

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
        db.collection(collection).add(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        store = _memory_store_test if collection == TEST_COLLECTION else _memory_store
        store.append(record)


def get_heatmap_data(cohort: Optional[str] = None) -> dict:
    """Aggregate results into a 6x5 count grid.

    When cohort is provided, only results matching that cohort are counted.
    The global heatmap (no cohort) only includes real data, never test data.
    """
    # Normalize cohort filter
    if cohort:
        cohort = cohort.strip().lower()

    collection = _collection_for(cohort)

    counts = {}
    for level in range(6):
        for stage in ["E", "P", "I", "A", "S"]:
            counts[f"{level}_{stage}"] = 0

    total = 0

    if _is_enabled():
        db = _get_client()
        query = db.collection(collection)
        if cohort:
            query = query.where("cohort", "==", cohort)
        docs = query.select(["cell_key"]).stream()
        for doc in docs:
            key = doc.to_dict().get("cell_key")
            if key in counts:
                counts[key] += 1
                total += 1
    else:
        store = _memory_store_test if collection == TEST_COLLECTION else _memory_store
        for record in store:
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


def clear_test_data() -> int:
    """Delete all documents in the test collection. Returns count deleted."""
    if not _is_enabled():
        count = len(_memory_store_test)
        _memory_store_test.clear()
        return count

    db = _get_client()
    docs = db.collection(TEST_COLLECTION).select([]).stream()
    count = 0
    batch = db.batch()
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()
    if count % 500 != 0:
        batch.commit()
    return count

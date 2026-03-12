"""Firestore storage for anonymous assessment results and feedback.

Uses Firestore when FIRESTORE_ENABLED=true, otherwise falls back to
an in-memory list (useful for local dev and demo deployments).

Test cohorts are stored in a separate collection so the global heatmap
only shows real assessment data. Test cohort heatmaps still work.
"""

import os
import uuid
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
    "sxsw-2026-tester", "sxsw-2026-test-group", "other-test-group",
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
    answers: Optional[dict] = None,
    sae_distribution: Optional[dict] = None,
    epias_distribution: Optional[dict] = None,
    referrer: Optional[str] = None,
    ua: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_medium: Optional[str] = None,
    utm_campaign: Optional[str] = None,
) -> None:
    """Store a single anonymous assessment result."""
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
        "app_version": "1.1",
    }

    # Rich telemetry fields — all optional
    if answers:
        record["answers"] = answers
    if sae_distribution:
        record["sae_distribution"] = sae_distribution
    if epias_distribution:
        record["epias_distribution"] = epias_distribution
    if referrer:
        record["referrer"] = referrer[:500]
    if ua:
        record["ua"] = ua[:300]
    if utm_source:
        record["utm_source"] = utm_source[:100]
    if utm_medium:
        record["utm_medium"] = utm_medium[:100]
    if utm_campaign:
        record["utm_campaign"] = utm_campaign[:100]

    if _is_enabled():
        from google.cloud import firestore as fs
        db = _get_client()
        record["timestamp"] = fs.SERVER_TIMESTAMP
        db.collection(collection).add(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        store = _memory_store_test if collection == TEST_COLLECTION else _memory_store
        store.append(record)


def get_heatmap_data(
    cohort: Optional[str] = None, include_test: bool = False
) -> dict:
    """Aggregate results into a 6x5 count grid.

    When cohort is provided, only results matching that cohort are counted.
    When include_test is True, test collection data is merged into the counts.
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

    # Determine which collections to query
    collections_to_query = [collection]
    if include_test and collection == COLLECTION:
        collections_to_query.append(TEST_COLLECTION)

    if _is_enabled():
        db = _get_client()
        for coll in collections_to_query:
            query = db.collection(coll)
            if cohort:
                query = query.where("cohort", "==", cohort)
            docs = query.select(["cell_key"]).stream()
            for doc in docs:
                key = doc.to_dict().get("cell_key")
                if key in counts:
                    counts[key] += 1
                    total += 1
    else:
        for coll in collections_to_query:
            store = _memory_store_test if coll == TEST_COLLECTION else _memory_store
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
        "include_test": include_test,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_analytics_data(cohort: Optional[str] = None, include_test: bool = False) -> dict:
    """Rich aggregated analytics for the admin dashboard.

    Returns distributions by level, stage, role, cohort, date, UTM source,
    and a recent-submissions list. Never returns PII — UA is bucketed to
    device type, answers are aggregate-only.
    """
    from collections import Counter, defaultdict

    if cohort:
        cohort = cohort.strip().lower()

    collection = _collection_for(cohort)
    collections_to_query = [collection]
    if include_test and collection == COLLECTION:
        collections_to_query.append(TEST_COLLECTION)

    by_level: Counter = Counter()
    by_stage: Counter = Counter()
    by_role: Counter = Counter()
    by_cohort: Counter = Counter()
    by_date: Counter = Counter()
    by_utm_source: Counter = Counter()
    by_utm_campaign: Counter = Counter()
    by_device: Counter = Counter()
    total = 0
    recent = []

    def _device(ua: str) -> str:
        ua = (ua or '').lower()
        if any(x in ua for x in ('iphone', 'android', 'mobile', 'ipad')):
            return 'mobile'
        return 'desktop'

    if _is_enabled():
        db = _get_client()
        for coll in collections_to_query:
            query = db.collection(coll)
            if cohort:
                query = query.where("cohort", "==", cohort)
            docs = query.order_by("timestamp", direction="DESCENDING").stream()
            for doc in docs:
                d = doc.to_dict()
                total += 1
                by_level[d.get("sae_level", "?")] += 1
                by_stage[d.get("epias_stage", "?")] += 1
                by_role[d.get("role") or "not specified"] += 1
                by_cohort[d.get("cohort") or "anonymous"] += 1
                by_utm_source[d.get("utm_source") or "direct"] += 1
                by_utm_campaign[d.get("utm_campaign") or "—"] += 1
                by_device[_device(d.get("ua", ""))] += 1
                ts = d.get("timestamp")
                if ts:
                    try:
                        date_str = ts.strftime("%Y-%m-%d")
                        by_date[date_str] += 1
                    except Exception:
                        pass
                if len(recent) < 50:
                    recent.append({
                        "sae_level": d.get("sae_level"),
                        "epias_stage": d.get("epias_stage"),
                        "cohort": d.get("cohort"),
                        "role": d.get("role"),
                        "age_range": d.get("age_range"),
                        "utm_source": d.get("utm_source"),
                        "utm_campaign": d.get("utm_campaign"),
                        "timestamp": ts.strftime("%Y-%m-%d %H:%M") if ts else None,
                    })
    else:
        for coll in collections_to_query:
            store = _memory_store_test if coll == TEST_COLLECTION else _memory_store
            for d in reversed(store):
                if cohort and d.get("cohort") != cohort:
                    continue
                total += 1
                by_level[d.get("sae_level", "?")] += 1
                by_stage[d.get("epias_stage", "?")] += 1
                by_role[d.get("role") or "not specified"] += 1
                by_cohort[d.get("cohort") or "anonymous"] += 1
                by_utm_source[d.get("utm_source") or "direct"] += 1
                by_utm_campaign[d.get("utm_campaign") or "—"] += 1
                by_device[_device(d.get("ua", ""))] += 1
                ts = d.get("timestamp", "")
                if ts:
                    by_date[ts[:10]] += 1
                if len(recent) < 50:
                    recent.append({
                        "sae_level": d.get("sae_level"),
                        "epias_stage": d.get("epias_stage"),
                        "cohort": d.get("cohort"),
                        "role": d.get("role"),
                        "age_range": d.get("age_range"),
                        "utm_source": d.get("utm_source"),
                        "utm_campaign": d.get("utm_campaign"),
                        "timestamp": ts[:16] if ts else None,
                    })

    # Sort date series chronologically
    sorted_dates = sorted(by_date.keys())

    return {
        "total": total,
        "by_level": dict(sorted(by_level.items())),
        "by_stage": {k: by_stage[k] for k in ["E", "P", "I", "A", "S"] if k in by_stage},
        "by_role": dict(by_role.most_common()),
        "by_cohort": dict(by_cohort.most_common(20)),
        "by_utm_source": dict(by_utm_source.most_common(10)),
        "by_utm_campaign": dict(by_utm_campaign.most_common(10)),
        "by_device": dict(by_device),
        "by_date": {d: by_date[d] for d in sorted_dates},
        "recent": recent,
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


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

FEEDBACK_COLLECTION = "feedback"
_feedback_store: list[dict] = []


def store_feedback(
    category: str, message: str, page: str, user_agent: str
) -> str:
    """Store user feedback, return its UUID."""
    fb_id = str(uuid.uuid4())
    record = {
        "id": fb_id,
        "category": category,
        "message": message,
        "page": page,
        "user_agent": user_agent,
        "status": "new",
    }

    if _is_enabled():
        from google.cloud import firestore as fs

        db = _get_client()
        record["timestamp"] = fs.SERVER_TIMESTAMP
        db.collection(FEEDBACK_COLLECTION).document(fb_id).set(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        _feedback_store.append(record)

    return fb_id


def get_feedback(fb_id: str) -> Optional[dict]:
    """Get a single feedback item by ID."""
    if _is_enabled():
        db = _get_client()
        doc = db.collection(FEEDBACK_COLLECTION).document(fb_id).get()
        return doc.to_dict() if doc.exists else None
    else:
        for item in _feedback_store:
            if item["id"] == fb_id:
                return dict(item)
        return None


def update_feedback(fb_id: str, message: str, category: str) -> bool:
    """User edits their own feedback (identified by UUID)."""
    if _is_enabled():
        db = _get_client()
        ref = db.collection(FEEDBACK_COLLECTION).document(fb_id)
        if not ref.get().exists:
            return False
        ref.update({"message": message, "category": category})
        return True
    else:
        for item in _feedback_store:
            if item["id"] == fb_id:
                item["message"] = message
                item["category"] = category
                return True
        return False


def list_feedback() -> list[dict]:
    """All feedback, newest first."""
    if _is_enabled():
        db = _get_client()
        docs = (
            db.collection(FEEDBACK_COLLECTION)
            .order_by("timestamp", direction="DESCENDING")
            .stream()
        )
        return [doc.to_dict() for doc in docs]
    else:
        return sorted(
            _feedback_store,
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )


def update_feedback_status(fb_id: str, status: str) -> bool:
    """Admin sets feedback status (new / reviewed / resolved)."""
    if status not in ("new", "reviewed", "resolved"):
        return False

    if _is_enabled():
        db = _get_client()
        ref = db.collection(FEEDBACK_COLLECTION).document(fb_id)
        if not ref.get().exists:
            return False
        ref.update({"status": status})
        return True
    else:
        for item in _feedback_store:
            if item["id"] == fb_id:
                item["status"] = status
                return True
        return False

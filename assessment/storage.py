"""Firestore storage for anonymous assessment results and feedback.

Uses Firestore when FIRESTORE_ENABLED=true, otherwise falls back to
an in-memory list (useful for local dev and demo deployments).

Test cohorts are stored in a separate collection so the global heatmap
only shows real assessment data. Test cohort heatmaps still work.
"""

import os
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Simple TTL cache for expensive Firestore aggregation queries.
# Prevents full-collection scans on every page load.
# ---------------------------------------------------------------------------
_cache_lock = threading.Lock()
_cache: dict[str, tuple[float, dict]] = {}  # key -> (expires_at, data)
_CACHE_TTL = 30  # seconds — fresh enough for live heatmap, avoids scan storms


def _cache_get(key: str):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and entry[0] > time.monotonic():
            return entry[1]
    return None


def _cache_set(key: str, data: dict):
    with _cache_lock:
        _cache[key] = (time.monotonic() + _CACHE_TTL, data)


def _is_enabled():
    return os.environ.get("FIRESTORE_ENABLED", "").lower() in ("1", "true")


COLLECTION = "assessment_results"
TEST_COLLECTION = "assessment_results_test"

# Cohort codes that route to the test collection.
# Configure via TEST_COHORTS env var (comma-separated) or hardcode here.
_DEFAULT_TEST_COHORTS = {
    # NOTE: sxsw-2026, linkedin-maeda, sxsw-livestream are REAL production
    # cohorts — do NOT include them here.  They were moved out before the
    # SXSW 2026 launch so submissions appear in the main heatmap.
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
    Results are cached for _CACHE_TTL seconds to avoid full-collection scans.
    """
    # Normalize cohort filter
    if cohort:
        cohort = cohort.strip().lower()

    cache_key = f"heatmap:{cohort or ''}:{include_test}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

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
                rec_cohort = record.get("cohort")
                if cohort:
                    if rec_cohort != cohort:
                        continue
                else:
                    # Global view: only count records with no cohort
                    if rec_cohort is not None:
                        continue
                key = record.get("cell_key")
                if key in counts:
                    counts[key] += 1
                    total += 1

    result = {
        "counts": counts,
        "total": total,
        "cohort": cohort,
        "include_test": include_test,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _cache_set(cache_key, result)
    return result


# ---------------------------------------------------------------------------
# V2 Tree Assessment — separate storage with 3D coordinates
# (root_depth, canopy_width, canopy_height) instead of flat (sae, stage).
# ---------------------------------------------------------------------------

TREE_COLLECTION = "tree_results"
_tree_store: list[dict] = []
_seeding = False  # Set True during bulk seed to skip per-record forest rebuilds

# Directory for individually-generated tree SVGs
import pathlib as _pathlib
_FOREST_TREE_DIR = _pathlib.Path(__file__).parent / "static" / "trees" / "forest"
_FOREST_TREE_DIR.mkdir(parents=True, exist_ok=True)


def _generate_tree_svg(rd: int, cw: int, ch: int, seed: int, filename: str) -> None:
    """Generate a unique organism SVG via the Node.js tree engine."""
    import subprocess
    script = _pathlib.Path(__file__).parent / "scripts" / "generate_one_tree.js"
    out_path = _FOREST_TREE_DIR / filename
    try:
        subprocess.run(
            ["node", str(script), str(rd), str(cw), str(ch), str(seed), str(out_path)],
            check=True, timeout=10, capture_output=True,
        )
    except Exception:
        # Fall back to copying the template organism SVG
        template = _pathlib.Path(__file__).parent / "static" / "trees" / "org" / f"r{rd}_c{cw}_h{ch}.svg"
        if template.exists():
            import shutil
            shutil.copy2(template, out_path)


def store_tree_result(
    root_depth: int,
    canopy_width: int,
    canopy_height: int,
    *,
    tree_id: Optional[str] = None,
    session_id: Optional[str] = None,
    cohort: Optional[str] = None,
    role: Optional[str] = None,
    balance: Optional[str] = None,
    tree_species: Optional[str] = None,
    root_stage: Optional[str] = None,
    canopy_stage: Optional[str] = None,
    answers: Optional[dict] = None,
    referrer: Optional[str] = None,
    ua: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_medium: Optional[str] = None,
    utm_campaign: Optional[str] = None,
) -> None:
    """Store a v2 tree assessment result with full 3D coordinates.

    If session_id is provided, generates a unique organism SVG seeded by it.
    Otherwise uses the template organism SVG for that (rd, cw, ch) combination.
    """
    if cohort:
        cohort = cohort.strip().lower()

    tree_key = f"r{root_depth}_c{canopy_width}_h{canopy_height}"

    # Generate unique SVG if we have a session ID
    if session_id:
        # Deterministic seed from session_id string
        seed = abs(hash(session_id)) % 2147483647 or 1
        svg_filename = f"{session_id}.svg"
        _generate_tree_svg(root_depth, canopy_width, canopy_height, seed, svg_filename)
    else:
        svg_filename = None

    record = {
        "root_depth": root_depth,
        "canopy_width": canopy_width,
        "canopy_height": canopy_height,
        "tree_key": tree_key,
        "svg_filename": svg_filename,
        "cohort": cohort or None,
        "role": role or None,
        "balance": balance or None,
        "tree_species": tree_species or None,
        "root_stage": root_stage or None,
        "canopy_stage": canopy_stage or None,
        "status": "complete",
        "app_version": "2.0",
    }

    if tree_id:
        record["tree_id"] = tree_id
    if answers:
        record["answers"] = answers
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
        # If tree_id exists, update the existing partial doc
        if tree_id:
            docs = list(db.collection(TREE_COLLECTION)
                         .where("tree_id", "==", tree_id)
                         .limit(1)
                         .stream())
            if docs:
                docs[0].reference.update(record)
            else:
                db.collection(TREE_COLLECTION).add(record)
        else:
            db.collection(TREE_COLLECTION).add(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        if tree_id:
            # Update existing in-memory record
            for i, rec in enumerate(_tree_store):
                if rec.get("tree_id") == tree_id:
                    rec.update(record)
                    break
            else:
                _tree_store.append(record)
        else:
            _tree_store.append(record)

    # Rebuild the forest SVG asset (skip during bulk seeding)
    if not _seeding:
        _rebuild_forest_svg(cohort)


# ---------------------------------------------------------------------------
# Tree ID — resumable assessment with return codes
# ---------------------------------------------------------------------------

_TREE_ID_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no O/0/I/1


def generate_tree_id() -> str:
    """Generate a unique TREE-XXXX ID, checking for collisions."""
    import random
    for _ in range(50):
        code = "TREE-" + "".join(random.choices(_TREE_ID_CHARS, k=4))
        if get_tree_progress(code) is None:
            return code
    # Extremely unlikely — extend to 5 chars
    return "TREE-" + "".join(random.choices(_TREE_ID_CHARS, k=5))


def save_tree_progress(
    tree_id: str,
    stage: str,
    answers: dict,
    *,
    role: Optional[str] = None,
    cohort: Optional[str] = None,
) -> None:
    """Save partial assessment progress at a stage boundary.

    Called after each stage (root, sae, canopy) completes.
    Creates the document on first call, upserts on subsequent calls.
    """
    if cohort:
        cohort = cohort.strip().lower()

    completed_stages_field = "completed_stages"

    if _is_enabled():
        from google.cloud import firestore as fs
        db = _get_client()
        # Find existing doc by tree_id
        docs = list(db.collection(TREE_COLLECTION)
                     .where("tree_id", "==", tree_id)
                     .limit(1)
                     .stream())
        update = {
            "tree_id": tree_id,
            "status": "partial",
            "answers": answers,
            "role": role,
            "cohort": cohort or None,
            "updated_at": fs.SERVER_TIMESTAMP,
        }
        if docs:
            doc_ref = docs[0].reference
            existing = docs[0].to_dict()
            stages = existing.get(completed_stages_field, [])
            if stage not in stages:
                stages.append(stage)
            update[completed_stages_field] = stages
            doc_ref.update(update)
        else:
            update[completed_stages_field] = [stage]
            update["timestamp"] = fs.SERVER_TIMESTAMP
            db.collection(TREE_COLLECTION).add(update)
    else:
        # In-memory fallback
        existing = None
        for rec in _tree_store:
            if rec.get("tree_id") == tree_id:
                existing = rec
                break
        if existing:
            stages = existing.get(completed_stages_field, [])
            if stage not in stages:
                stages.append(stage)
            existing.update({
                "status": "partial",
                "answers": answers,
                "role": role,
                "cohort": cohort or None,
                completed_stages_field: stages,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
        else:
            _tree_store.append({
                "tree_id": tree_id,
                "status": "partial",
                "answers": answers,
                "role": role,
                "cohort": cohort or None,
                completed_stages_field: [stage],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })


def get_tree_progress(tree_id: str) -> Optional[dict]:
    """Fetch a tree record by its tree_id. Returns None if not found."""
    if not tree_id or not tree_id.startswith("TREE-"):
        return None

    if _is_enabled():
        db = _get_client()
        docs = list(db.collection(TREE_COLLECTION)
                     .where("tree_id", "==", tree_id)
                     .limit(1)
                     .stream())
        if docs:
            return docs[0].to_dict()
        return None
    else:
        for rec in _tree_store:
            if rec.get("tree_id") == tree_id:
                return rec
        return None


def get_forest_data(cohort: Optional[str] = None) -> dict:
    """Return individual tree records for the forest renderer.

    Returns:
        {
            "trees": [
                {"tree_key": "r3_c2_h3", "rd": 3, "cw": 2, "ch": 3,
                 "svg_filename": "abc123.svg" or None, "balance": "balanced"},
                ...
            ],
            "total": 500,
            "cohort": None,
        }
    """
    if cohort:
        cohort = cohort.strip().lower()

    cache_key = f"forest:{cohort or ''}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    trees: list[dict] = []

    if _is_enabled():
        db = _get_client()
        query = db.collection(TREE_COLLECTION)
        if cohort:
            query = query.where("cohort", "==", cohort)
        docs = query.select(["tree_key", "root_depth", "canopy_width",
                             "canopy_height", "svg_filename", "balance"]).stream()
        for doc in docs:
            d = doc.to_dict()
            trees.append({
                "tree_key": d.get("tree_key"),
                "rd": d.get("root_depth"),
                "cw": d.get("canopy_width"),
                "ch": d.get("canopy_height"),
                "svg_filename": d.get("svg_filename"),
                "balance": d.get("balance"),
            })
    else:
        for record in _tree_store:
            rec_cohort = record.get("cohort")
            if cohort:
                if rec_cohort != cohort:
                    continue
            trees.append({
                "tree_key": record.get("tree_key"),
                "rd": record.get("root_depth"),
                "cw": record.get("canopy_width"),
                "ch": record.get("canopy_height"),
                "svg_filename": record.get("svg_filename"),
                "balance": record.get("balance"),
            })

    result = {
        "trees": trees,
        "total": len(trees),
        "cohort": cohort,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _cache_set(cache_key, result)
    return result


# ── Pre-rendered forest SVG assets ──
# Built once per submission, persisted to disk.
# Page views just read the file — zero computation.

_FOREST_SVG_DIR = _pathlib.Path(__file__).parent / "static" / "forest-svg"
_FOREST_SVG_DIR.mkdir(parents=True, exist_ok=True)


def _forest_svg_path(cohort: Optional[str] = None, mode: str = "trees") -> _pathlib.Path:
    slug = (cohort or "global").strip().lower().replace("/", "_")
    return _FOREST_SVG_DIR / f"{slug}_{mode}.svg"


def _forest_stats_path(cohort: Optional[str] = None) -> _pathlib.Path:
    slug = (cohort or "global").strip().lower().replace("/", "_")
    return _FOREST_SVG_DIR / f"{slug}.json"


def _rebuild_forest_svg(cohort: Optional[str] = None, *, sync: bool = False) -> None:
    """Regenerate the persisted forest SVG for a given cohort (or global).

    By default runs in a background thread so assessment submissions
    are not delayed. Pass sync=True for seed-time or first-load builds.
    """
    def _do_rebuild():
        # Invalidate data cache so get_forest_data re-queries
        with _cache_lock:
            to_drop = [k for k in _cache if k.startswith("forest:")]
            for k in to_drop:
                del _cache[k]

        from assessment.forest_renderer import render_forest_svg
        forest_data = get_forest_data(cohort=cohort)

        import json as _json
        stats_path = _forest_stats_path(cohort)

        # Build both modes — write directly (Windows doesn't like tmp+rename)
        for mode in ("trees", "forest"):
            svg_str, stats = render_forest_svg(forest_data, mode=mode)
            _forest_svg_path(cohort, mode).write_text(svg_str, encoding="utf-8")

        # Stats are the same for both modes
        stats_path.write_text(_json.dumps(stats), encoding="utf-8")

    if sync:
        _do_rebuild()
    else:
        t = threading.Thread(target=_do_rebuild, daemon=True)
        t.start()


def get_forest_svg(cohort: Optional[str] = None) -> tuple[str, str, dict]:
    """Return both persisted forest SVGs and stats.

    Reads from disk. If files don't exist yet, builds synchronously.

    Returns:
        (trees_svg, forest_svg, stats_dict)
    """
    import json as _json
    trees_path = _forest_svg_path(cohort, "trees")
    forest_path = _forest_svg_path(cohort, "forest")
    stats_path = _forest_stats_path(cohort)

    if not trees_path.exists():
        _rebuild_forest_svg(cohort, sync=True)

    _placeholder = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50" y="50" text-anchor="middle" fill="#999" font-size="8">Building...</text></svg>'

    def _read(p):
        try:
            return p.read_text(encoding="utf-8")
        except FileNotFoundError:
            return _placeholder

    trees_svg = _read(trees_path)
    forest_svg = _read(forest_path)

    try:
        stats = _json.loads(stats_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        stats = {"total": 0, "balance_counts": {}}

    return trees_svg, forest_svg, stats


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
                d_cohort = d.get("cohort")
                if cohort:
                    if d_cohort != cohort:
                        continue
                else:
                    if d_cohort is not None:
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

    # Compute weighted averages server-side (Jinja2 can't do this reliably)
    avg_level = 0.0
    if total > 0:
        avg_level = sum(int(lvl) * cnt for lvl, cnt in by_level.items()) / total

    stage_index = {"E": 0, "P": 1, "I": 2, "A": 3, "S": 4}
    avg_stage_idx = 0
    if total > 0:
        weighted = sum(stage_index.get(s, 0) * cnt for s, cnt in by_stage.items())
        avg_stage_idx = round(weighted / total)
    avg_stage = ["E", "P", "I", "A", "S"][min(max(avg_stage_idx, 0), 4)]

    return {
        "total": total,
        "by_level": dict(sorted(by_level.items())),
        "by_stage": {k: by_stage[k] for k in ["E", "P", "I", "A", "S"] if k in by_stage},
        "avg_level": round(avg_level, 1),
        "avg_stage": avg_stage,
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


# ---------------------------------------------------------------------------
# Analytics Events — lightweight client-side event tracking
# ---------------------------------------------------------------------------

EVENTS_COLLECTION = "events"
_events_store: list[dict] = []

# Valid event names (whitelist to prevent abuse)
_VALID_EVENTS = {
    "page_view",
    "assess_start",         # user clicks "Begin" on intake
    "intake_complete",      # role selected, moving to SAE
    "sae_answer",           # answered a SAE question
    "sae_complete",         # finished all SAE questions
    "epias_answer",         # answered an EPIAS question
    "epias_complete",       # finished all EPIAS questions
    "assess_submit",        # assessment submitted successfully
    "assess_abandon",       # left page with incomplete assessment
    "results_view",         # viewed results page
    "results_share",        # clicked share/copy/download on results
    "framework_view",       # viewed a framework tab
    "heatmap_interact",     # clicked a heatmap cell
}


def store_event(
    event: str,
    session_id: str,
    props: Optional[dict] = None,
    ua: Optional[str] = None,
) -> bool:
    """Store a single analytics event. Returns True on success."""
    if event not in _VALID_EVENTS:
        return False

    record = {
        "event": event,
        "session_id": session_id[:64],
        "props": props or {},
        "ua": (ua or "")[:300],
    }

    if _is_enabled():
        from google.cloud import firestore as fs
        db = _get_client()
        record["timestamp"] = fs.SERVER_TIMESTAMP
        db.collection(EVENTS_COLLECTION).add(record)
    else:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        _events_store.append(record)

    return True


def get_event_analytics(hours: int = 120) -> dict:
    """Aggregate event data for the admin dashboard.

    Returns funnel counts, page view counts, hourly time series,
    device breakdown, and session-level funnel analysis.
    Default window: 120 hours (5 days).
    """
    from collections import Counter, defaultdict

    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)

    by_event: Counter = Counter()
    by_page: Counter = Counter()
    by_device: Counter = Counter()
    by_hour: Counter = Counter()
    by_date: Counter = Counter()
    sessions: dict[str, set[str]] = defaultdict(set)  # session_id -> set of events
    total = 0

    def _device(props: dict, ua: str) -> str:
        # Prefer client-side detection (in props) over server-side UA parsing,
        # because _short_ua() strips mobile indicators from the UA string.
        client_device = (props.get("device") or "").lower()
        if client_device in ("mobile", "desktop"):
            return client_device
        ua = (ua or "").lower()
        if any(x in ua for x in ("iphone", "android", "mobile", "ipad")):
            return "mobile"
        return "desktop"

    if _is_enabled():
        db = _get_client()
        query = db.collection(EVENTS_COLLECTION).order_by(
            "timestamp", direction="DESCENDING"
        )
        for doc in query.stream():
            d = doc.to_dict()
            ts = d.get("timestamp")
            if ts:
                try:
                    ts_epoch = ts.timestamp()
                    if ts_epoch < cutoff:
                        break  # ordered desc, so we can stop
                except Exception:
                    continue
            total += 1
            evt = d.get("event", "")
            by_event[evt] += 1
            props = d.get("props", {})
            if props.get("path"):
                by_page[props["path"]] += 1
            by_device[_device(props, d.get("ua", ""))] += 1
            sid = d.get("session_id", "")
            if sid:
                sessions[sid].add(evt)
            if ts:
                try:
                    by_hour[ts.strftime("%Y-%m-%d %H:00")] += 1
                    by_date[ts.strftime("%Y-%m-%d")] += 1
                except Exception:
                    pass
    else:
        for d in reversed(_events_store):
            ts_str = d.get("timestamp", "")
            if ts_str:
                try:
                    ts_dt = datetime.fromisoformat(ts_str)
                    if ts_dt.timestamp() < cutoff:
                        break
                except Exception:
                    pass
            total += 1
            evt = d.get("event", "")
            by_event[evt] += 1
            props = d.get("props", {})
            if props.get("path"):
                by_page[props["path"]] += 1
            by_device[_device(props, d.get("ua", ""))] += 1
            sid = d.get("session_id", "")
            if sid:
                sessions[sid].add(evt)
            if ts_str:
                by_date[ts_str[:10]] += 1
                by_hour[ts_str[:13] + ":00"] += 1

    # Build funnel: how many sessions reached each stage
    funnel_stages = [
        ("page_view", "Visited"),
        ("assess_start", "Started Assessment"),
        ("intake_complete", "Chose Role"),
        ("sae_complete", "Finished Part 1 (SAE)"),
        ("epias_complete", "Finished Part 2 (EPIAS)"),
        ("assess_submit", "Submitted"),
        ("results_view", "Viewed Results"),
        ("results_share", "Shared Results"),
    ]
    funnel = []
    for event_name, label in funnel_stages:
        count = sum(1 for evts in sessions.values() if event_name in evts)
        funnel.append({"event": event_name, "label": label, "sessions": count})

    return {
        "total_events": total,
        "unique_sessions": len(sessions),
        "by_event": dict(by_event.most_common()),
        "by_page": dict(by_page.most_common(20)),
        "by_device": dict(by_device),
        "by_date": {d: by_date[d] for d in sorted(by_date.keys())},
        "by_hour": {h: by_hour[h] for h in sorted(by_hour.keys())[-48:]},  # last 48 hours
        "funnel": funnel,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

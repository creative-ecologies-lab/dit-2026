"""Delete documents from assessment_results where cohort is null/None.

Exports deleted docs to a JSON backup before deleting.

Usage (from assessment/ directory):
    FIRESTORE_ENABLED=true python scripts/clear_null_cohort.py --dry-run
    FIRESTORE_ENABLED=true python scripts/clear_null_cohort.py
"""
import io
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("FIRESTORE_ENABLED", "true")

import argparse
from google.cloud import firestore

COLLECTION = "assessment_results"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no deletions")
    args = parser.parse_args()

    db = firestore.Client()
    coll = db.collection(COLLECTION)

    # Query docs where cohort is null
    null_cohort_docs = list(coll.where("cohort", "==", None).select(["cohort", "sae_level", "epias_stage", "cell_key", "role", "age_range", "timestamp"]).stream())

    print(f"Documents with null cohort in '{COLLECTION}': {len(null_cohort_docs)}")

    if not null_cohort_docs:
        print("Nothing to delete.")
        return

    # Show sample
    print("\nSample (up to 10):")
    for doc in null_cohort_docs[:10]:
        d = doc.to_dict()
        print(f"  {doc.id}: cell={d.get('cell_key')} role={d.get('role')} age={d.get('age_range')} ts={d.get('timestamp')}")

    if args.dry_run:
        print(f"\n[Dry run] Would delete {len(null_cohort_docs)} documents.")
        return

    # Export backup before deleting
    backup = []
    for doc in null_cohort_docs:
        d = doc.to_dict()
        d["_doc_id"] = doc.id
        # Convert Firestore DatetimeWithNanoseconds to string
        if hasattr(d.get("timestamp"), "isoformat"):
            d["timestamp"] = d["timestamp"].isoformat()
        backup.append(d)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(os.path.dirname(__file__), f"null_cohort_backup_{ts}.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, default=str)
    print(f"\nBackup written: {backup_path}")

    # Delete in batches of 500
    count = 0
    batch = db.batch()
    for doc in null_cohort_docs:
        batch.delete(doc.reference)
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Deleted {count}...")
    if count % 500 != 0:
        batch.commit()

    print(f"\nDeleted {count} null-cohort documents from '{COLLECTION}'.")

    # Show remaining count
    remaining = coll.select([]).stream()
    total_remaining = sum(1 for _ in remaining)
    print(f"Remaining documents in '{COLLECTION}': {total_remaining}")


if __name__ == "__main__":
    main()

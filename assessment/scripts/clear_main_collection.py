"""One-off script to clear the main assessment_results collection.

Use this when the main collection contains only simulated data that
needs to be wiped before real users start taking the assessment.

Usage:
    cd assessment
    FIRESTORE_ENABLED=true python scripts/clear_main_collection.py
"""
import os
import sys

os.environ.setdefault("FIRESTORE_ENABLED", "true")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from google.cloud import firestore

COLLECTION = "assessment_results"


def clear_collection():
    db = firestore.Client()
    docs = db.collection(COLLECTION).select([]).stream()
    count = 0
    batch = db.batch()
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Deleted {count} documents...")
    if count % 500 != 0:
        batch.commit()
    return count


if __name__ == "__main__":
    print(f"Clearing Firestore collection: {COLLECTION}")
    print("This will delete ALL documents in the main collection.")
    deleted = clear_collection()
    print(f"Done. Deleted {deleted} documents.")

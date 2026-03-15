"""
apply_revised_stems.py

Applies the JSON output from rewrite_epias_stems.py into questions.py.

Usage (from the assessment/ directory):
    python scripts/apply_revised_stems.py                        # uses stems_revised.json
    python scripts/apply_revised_stems.py --input stems_v2.json  # custom input file
    python scripts/apply_revised_stems.py --dry-run              # print diff, don't write

The script does a targeted string replacement: finds each current question stem
in questions.py by exact match and replaces it with the new stem. It won't touch
options, IDs, dimensions, or anything else.
"""

import argparse
import io
import json
import os
import re
import sys

# Force UTF-8 on Windows console so unicode in stems doesn't crash print()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assessment.questions import EPIAS_QUESTIONS_DESIGN, EPIAS_QUESTIONS_UXR


def build_id_to_stem_map() -> dict[str, str]:
    """Return {question_id: current_stem} for all EPIAS questions."""
    result = {}
    for source in (EPIAS_QUESTIONS_DESIGN, EPIAS_QUESTIONS_UXR):
        for level_qs in source.values():
            for q in level_qs:
                result[q["id"]] = q["question"]
    return result


def main():
    parser = argparse.ArgumentParser(description="Apply revised EPIAS stems to questions.py")
    parser.add_argument("--input", default="scripts/stems_revised.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base, args.input)
    questions_path = os.path.join(base, "assessment", "questions.py")

    with open(input_path, "r", encoding="utf-8") as f:
        revised: dict[str, dict[str, str]] = json.load(f)

    # Flatten to {question_id: new_stem}
    flat: dict[str, str] = {}
    for track_data in revised.values():
        flat.update(track_data)

    # Skip errors
    flat = {k: v for k, v in flat.items() if not v.startswith("ERROR:")}

    id_to_old = build_id_to_stem_map()

    with open(questions_path, "r", encoding="utf-8") as f:
        content = f.read()

    applied = 0
    skipped = 0

    for qid, new_stem in flat.items():
        old_stem = id_to_old.get(qid)
        if not old_stem:
            print(f"SKIP (id not found): {qid}")
            skipped += 1
            continue

        # Match the full "question": "..." line as it appears in the file
        old_pattern = f'"question": "{old_stem}"'
        new_pattern = f'"question": "{new_stem}"'

        if old_pattern not in content:
            print(f"SKIP (stem not found in file): {qid}")
            print(f"  Looking for: {old_pattern[:90]}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"\n{qid}")
            print(f"  OLD: {old_stem[:90]}")
            print(f"  NEW: {new_stem}")
        else:
            content = content.replace(old_pattern, new_pattern, 1)
            print(f"  APPLIED: {qid}")
            applied += 1

    if not args.dry_run:
        # Backup original (content was already read into `content` variable above)
        backup_path = questions_path.replace(".py", "_backup.py")
        import shutil
        shutil.copy2(questions_path, backup_path)
        with open(questions_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nApplied {applied} stems. Skipped {skipped}.")
        print(f"Original backed up to: questions_backup.py")
        print(f"Updated: {questions_path}")
    else:
        print(f"\n[Dry run] Would apply {len(flat) - skipped} stems. Skipped {skipped}.")


if __name__ == "__main__":
    main()

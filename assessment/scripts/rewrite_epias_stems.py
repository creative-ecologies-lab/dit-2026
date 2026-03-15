"""
rewrite_epias_stems.py

Rewrites EPIAS question stems using GPT-5.1.

The problem: current stems ask "how do you [do the task]?" (behavioral framing),
but the options answer "how mature/transferable is your practice?" (maturity framing).
This mismatch means the question stem doesn't prime respondents to think about
the E→S spectrum — from initial personal exploration to setting organizational standards.

The fix: rewrite each stem so it frames the dimension as a practice maturity question,
not a task description. The options are kept exactly as-is.

Usage (from the assessment/ directory):
    python scripts/rewrite_epias_stems.py
    python scripts/rewrite_epias_stems.py --dry-run         # print stems, don't write
    python scripts/rewrite_epias_stems.py --track design    # one track only
    python scripts/rewrite_epias_stems.py --output stems_revised.json
"""

import argparse
import io
import json
import os
import sys
import time

# Force UTF-8 on Windows console so unicode in stems/options doesn't crash print()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from openai import OpenAI

# ---------------------------------------------------------------------------
# Path setup — run from assessment/ directory
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assessment.questions import (
    EPIAS_QUESTIONS_DESIGN,
    EPIAS_QUESTIONS_UXR,
    SAE_QUESTIONS_DESIGN,
    SAE_QUESTIONS_UXR,
)

# ---------------------------------------------------------------------------
# Rich context prompt — everything GPT-5.1 needs to understand the task
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert survey designer specializing in professional self-assessment \
instruments for product designers and UX researchers. You write concise, precise \
question stems for practice-maturity assessments.\
"""

# Injected once per question — matched to the working _example_run.py prompt
CONTEXT = """\
This is a self-assessment survey for product designers and UX researchers measuring \
AI practice maturity. Respondents first answer 6 SAE questions (like "Which best \
describes how you regularly use AI in your work?") that score them to a level L0-L5. \
They then see 5 EPIAS questions for their level. Each EPIAS question has 5 options \
ranging from E (still figuring it out, inconsistent) through P (reliable but personal), \
I (documented, others can follow it), A (packaged, teams run it without your help), \
to S (you set the org-wide standard and coach others).

The current EPIAS stems are too wordy -- they describe a specific scenario \
("When you get a vague request from a PM...") and read like "describe what you do." \
They should be short plain questions like the SAE ones: "Which best describes your X practice?"

Rules for the new stem:
- One plain question, 15 words or fewer
- Starts with "Which best describes..." or similar direct phrasing
- Names the specific dimension so the respondent knows what's being assessed
- No sub-clauses, no dashes, no explanation of the spectrum
- Reads naturally -- a person should understand it immediately

Good examples of the pattern:
  "Which best describes your design-handoff practice?"
  "Which best describes how you track AI-influenced design decisions?"
  "Which best describes your prompt organization practice?"
"""


def format_question_prompt(track: str, sae_level: int, q: dict) -> str:
    """Build the per-question user message."""
    options_text = "\n".join(
        f"  {opt['stage']}: {opt['text']}" for opt in q["options"]
    )
    return f"""\
{CONTEXT}

Now write a new stem for this question:

Track: {track}
SAE Level: L{sae_level}
Dimension: {q['dimension']}
Current stem: {q['question']}

Options the stem must introduce (DO NOT change these):
{options_text}

Return ONLY the new question stem -- no quotes, no explanation."""


def call_gpt51(client: OpenAI, prompt: str) -> str:
    """Call GPT-5.1 via Responses API and return the new stem text."""
    resp = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
        max_output_tokens=2000,
        reasoning={"effort": "medium"},
    )

    # Extract text from response
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text.strip()
    if hasattr(resp, "output") and resp.output:
        for block in resp.output:
            content = getattr(block, "content", None)
            if not content:
                continue
            for item in content:
                text = getattr(item, "text", None)
                if text:
                    return text.strip()
    raise ValueError(f"Could not extract text from response: {resp}")


def collect_questions(track: str) -> list[tuple[int, dict]]:
    """Return [(sae_level, question_dict), ...] for the given track."""
    source = EPIAS_QUESTIONS_DESIGN if track == "design" else EPIAS_QUESTIONS_UXR
    result = []
    for level in sorted(source.keys()):
        for q in source[level]:
            result.append((level, q))
    return result


def main():
    parser = argparse.ArgumentParser(description="Rewrite EPIAS question stems with GPT-5.1")
    parser.add_argument("--dry-run", action="store_true", help="Print results, don't write file")
    parser.add_argument("--track", choices=["design", "uxr", "both"], default="both")
    parser.add_argument(
        "--output",
        default="scripts/stems_revised.json",
        help="Output JSON path (relative to assessment/)",
    )
    parser.add_argument("--delay", type=float, default=1.5, help="Seconds between API calls")
    args = parser.parse_args()

    client = OpenAI()

    tracks = ["design", "uxr"] if args.track == "both" else [args.track]

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        args.output,
    )

    # Load any partial results from a previous interrupted run
    results: dict[str, dict[str, str]] = {}
    if not args.dry_run and os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"Resuming from existing file: {out_path}")

    for track in tracks:
        print(f"\n{'='*60}")
        print(f"Track: {track.upper()}")
        print(f"{'='*60}")
        if track not in results:
            results[track] = {}
        questions = collect_questions(track)

        for i, (sae_level, q) in enumerate(questions, 1):
            qid = q["id"]
            dim = q["dimension"]
            old_stem = q["question"]

            # Skip already-completed questions (resume support)
            if qid in results[track] and not results[track][qid].startswith("ERROR:"):
                print(f"\n[{i:02d}/{len(questions)}] L{sae_level} | {dim}  [SKIP — already done]")
                continue

            print(f"\n[{i:02d}/{len(questions)}] L{sae_level} | {dim}")
            print(f"  OLD: {old_stem[:90]}{'...' if len(old_stem) > 90 else ''}")

            prompt = format_question_prompt(
                track="Product Design" if track == "design" else "UX Research",
                sae_level=sae_level,
                q=q,
            )

            try:
                new_stem = call_gpt51(client, prompt)
                print(f"  NEW: {new_stem}")
                results[track][qid] = new_stem
            except Exception as e:
                print(f"  ERROR: {e}")
                results[track][qid] = f"ERROR: {e}"

            # Save after every question so a crash doesn't lose work
            if not args.dry_run:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

            if i < len(questions):
                time.sleep(args.delay)

    # Final save / dry-run output
    if not args.dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n\nResults written to: {out_path}")
        print("Review the output, then run apply_revised_stems.py to patch questions.py")
    else:
        print("\n\n[Dry run — no file written]")
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

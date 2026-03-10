#!/usr/bin/env python3
"""Evaluate generated EPIAS questions for Guttman overlap.

For each question, simulates 5 personas (one per EPIAS stage) and checks:
1. Does each persona pick exactly one option?
2. Does each persona pick the CORRECT option for their stage?
3. Do any personas report that multiple options feel true?

Usage:
    python scripts/evaluate_epias_questions.py [--input scripts/epias_generated.json]

Reads generated questions and runs LLM-based persona evaluation.
"""

import argparse
import json
import sys
from pathlib import Path

from openai import OpenAI

PERSONA_DESCRIPTIONS = {
    "E": (
        "You are a designer/researcher who is EXPLORING AI tools. You're still experimenting, "
        "results are inconsistent, and you haven't found reliable patterns yet. You mostly "
        "work alone and are learning. You have NOT developed personal systems that work "
        "reliably. You do NOT document your process for others."
    ),
    "P": (
        "You are a designer/researcher who is a PRACTITIONER with AI. You have reliable "
        "personal techniques that work consistently for you. BUT: your approach lives in "
        "your head — it's not documented, and others haven't adopted it. You do NOT have "
        "documented processes others can review. You have NOT built systems others use."
    ),
    "I": (
        "You are a designer/researcher who is an INTEGRATOR. Your work is documented, "
        "traceable, and reviewable by others. You can explain what AI contributed and why. "
        "BUT: you haven't built systems that others use independently. Others can review "
        "your work but don't run your systems without you."
    ),
    "A": (
        "You are a designer/researcher who is an ARCHITECT. You've built systems, templates, "
        "and processes that others use to get results WITHOUT your help. Your work scales "
        "beyond you. BUT: you don't set organizational standards or govern practice at "
        "the org level. You're not mentoring across the organization."
    ),
    "S": (
        "You are a designer/researcher who is a STEWARD. You set organizational standards, "
        "mentor others, and govern practice at the org level. Your frameworks define how "
        "the organization works. You are the most senior practitioner."
    ),
}

EVAL_SYSTEM_PROMPT = """\
You are role-playing a specific persona to test an assessment question. \
You must answer ONLY based on the persona description — not your own capabilities. \
Be strict about the persona's limitations."""


def evaluate_question(client: OpenAI, question: dict, persona_stage: str) -> dict:
    """Test one question with one persona. Returns evaluation result."""
    persona = PERSONA_DESCRIPTIONS[persona_stage]
    options_text = "\n".join(
        f"  {opt['stage']}: {opt['text']}" for opt in question["options"]
    )

    prompt = f"""\
You are playing this persona:
{persona}

Here is an assessment question:
"{question['question']}"

Options:
{options_text}

Instructions:
1. Read each option carefully from the perspective of your persona.
2. Which ONE option best matches your persona? Reply with just the letter (E, P, I, A, or S).
3. Are there any OTHER options that ALSO feel true for your persona? If yes, list them.

Reply in this exact JSON format (no markdown):
{{"selected": "<letter>", "also_true": ["<letter>", ...], "reasoning": "<one sentence>"}}"""

    resp = client.responses.create(
        model="gpt-5.2",
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": EVAL_SYSTEM_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
        max_output_tokens=300,
        reasoning={"effort": "medium"},
    )

    text = ""
    if hasattr(resp, "output_text") and resp.output_text:
        text = resp.output_text.strip()
    elif hasattr(resp, "output") and resp.output:
        for block in resp.output:
            if hasattr(block, "content"):
                for item in block.content:
                    if hasattr(item, "text"):
                        text = item.text.strip()

    # Strip markdown fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {"selected": "?", "also_true": [], "reasoning": f"Parse error: {text[:200]}"}

    return {
        "persona": persona_stage,
        "expected": persona_stage,
        "selected": result.get("selected", "?"),
        "also_true": result.get("also_true", []),
        "correct": result.get("selected", "?") == persona_stage,
        "overlap": len(result.get("also_true", [])) > 0,
        "reasoning": result.get("reasoning", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate EPIAS questions for overlap")
    parser.add_argument("--input", type=str, default="scripts/epias_generated.json",
                        help="Input file with generated questions")
    parser.add_argument("--track", choices=["design", "uxr", "both"], default="both")
    parser.add_argument("--level", type=int, choices=range(6), default=None)
    args = parser.parse_args()

    in_path = Path(__file__).parent.parent / args.input
    data = json.loads(in_path.read_text(encoding="utf-8"))

    client = OpenAI()

    tracks = ["DESIGN", "UXR"] if args.track == "both" else [args.track.upper()]
    stages = ["E", "P", "I", "A", "S"]

    total_tests = 0
    correct = 0
    overlaps = 0
    failures = []

    for track in tracks:
        track_key = f"EPIAS_QUESTIONS_{track}"
        if track_key not in data:
            print(f"Skipping {track_key} — not in input file", file=sys.stderr)
            continue

        levels = [str(args.level)] if args.level is not None else list(data[track_key].keys())

        for level_str in levels:
            questions = data[track_key][level_str]
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Evaluating {track} L{level_str} ({len(questions)} questions × 5 personas)", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

            for q in questions:
                print(f"\n  Q: {q['question']}", file=sys.stderr)

                for stage in stages:
                    result = evaluate_question(client, q, stage)
                    total_tests += 1

                    icon = "✓" if result["correct"] else "✗"
                    overlap_icon = " ⚠ OVERLAP" if result["overlap"] else ""
                    print(
                        f"    {icon} Persona {stage} → selected {result['selected']}"
                        f"{overlap_icon} — {result['reasoning']}",
                        file=sys.stderr,
                    )

                    if result["correct"]:
                        correct += 1
                    else:
                        failures.append({
                            "track": track,
                            "level": level_str,
                            "question_id": q["id"],
                            "question": q["question"],
                            **result,
                        })

                    if result["overlap"]:
                        overlaps += 1

    # Summary
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"RESULTS: {correct}/{total_tests} correct ({100*correct/max(total_tests,1):.0f}%)", file=sys.stderr)
    print(f"Overlaps (persona felt multiple options true): {overlaps}/{total_tests}", file=sys.stderr)

    if failures:
        print(f"\nFAILURES ({len(failures)}):", file=sys.stderr)
        for f in failures:
            print(
                f"  {f['track']} L{f['level']} {f['question_id']}: "
                f"persona {f['persona']} picked {f['selected']} (expected {f['expected']}) "
                f"— {f['reasoning']}",
                file=sys.stderr,
            )

    # Output structured results
    report = {
        "total_tests": total_tests,
        "correct": correct,
        "accuracy": round(correct / max(total_tests, 1), 3),
        "overlaps": overlaps,
        "overlap_rate": round(overlaps / max(total_tests, 1), 3),
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

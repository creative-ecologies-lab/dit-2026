#!/usr/bin/env python3
"""Generate EPIAS assessment questions using OpenAI GPT-5.2.

Uses contrastive anchoring so each EPIAS stage (E/P/I/A/S) is mutually
exclusive — a respondent at stage I should NOT feel that stage P also
applies.  Mirrors the approach used for the approved SAE questions.

Usage:
    python scripts/generate_epias_questions.py [--level N] [--track design|uxr|both]

Outputs JSON to stdout and saves to scripts/epias_generated.json
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

from openai import OpenAI

# ---------------------------------------------------------------------------
# Framework definitions (same as questions.py header)
# ---------------------------------------------------------------------------

SAE_LEVELS = {
    0: {
        "name": "Manual (L0)",
        "desc": "No AI used. Designer/researcher owns every step.",
        "epias_focus": "maturity of manual craft, process, documentation, knowledge sharing",
    },
    1: {
        "name": "AI-Assisted (L1)",
        "desc": "AI as chat tool — one task at a time, human types every prompt.",
        "epias_focus": "prompt organization, AI judgment, output consistency, traceability",
    },
    2: {
        "name": "Partially Automated (L2)",
        "desc": "Human gives spec, AI produces bounded deliverable. Human integrates.",
        "epias_focus": "spec clarity, integration quality, chunking skill, QA rigor, reusability",
    },
    3: {
        "name": "Guided Automation (L3)",
        "desc": "Multi-step AI workflows in IDE with checkpoints. Stops when human stops.",
        "epias_focus": "workflow reliability, context engineering, failure handling, tooling, decision ownership",
    },
    4: {
        "name": "Mostly Automated (L4)",
        "desc": "Agent harnesses with eval suites. Work continues when human steps away.",
        "epias_focus": "harness maturity, eval automation, system autonomy, shared infrastructure, governance",
    },
    5: {
        "name": "Full Automation (L5)",
        "desc": "AI runs end-to-end. Human sets goals and reviews exceptions.",
        "epias_focus": "goal-setting, oversight, trust calibration, system adaptation, accountability",
    },
}

EPIAS_STAGES = {
    "E": "Explorer — still experimenting, inconsistent results, learning what works",
    "P": "Practitioner — reliable personal approach, but it lives in my head / only I use it",
    "I": "Integrator — documented, traceable, reviewable by others",
    "A": "Architect — others use my systems and get results without my help",
    "S": "Steward — I set organizational standards, mentor others, govern practice",
}

# The approved SAE questions serve as style exemplars
SAE_EXEMPLARS = """
Example of GOOD contrastive options (from the approved SAE questions):

Q: "What is the most autonomous way you regularly use AI in your work?"
- L0: "I don't use AI tools in my work."
- L1: "I use AI for one task at a time — chat, generate, review, repeat."
- L2: "I give AI a spec and it produces usable pieces — I assemble and integrate them."
- L3: "I run multi-step AI workflows with checkpoints — work persists across sessions."
- L4: "I run autonomous AI systems that execute, evaluate, and self-correct without me present."
- L5: "AI handles my workflow end-to-end — I set goals and review exceptions."

Q: "How transferable is the most advanced AI setup you've built?"
- L0: "N/A — I don't use AI workflows."
- L1: "Not really — I have saved prompts I copy-paste, but nothing structured."
- L2: "For me — I maintain reusable templates and specs, but they're personal."
- L3: "For my team — I maintain shared workflows and context libraries others can run."
- L4: "For the org — I maintain production infrastructure others operate as a service."
- L5: "It transfers itself — self-improving pipelines that adapt to new users and contexts."

Notice how each option:
1. Contains a concrete behavioral anchor (what you actually DO)
2. Has a natural ceiling — picking it would feel wrong if you're at a higher level
3. Uses plain language, not jargon
4. Is one sentence, sometimes two short clauses joined by an em dash
"""

DESIGN_DOMAIN = """Domain: Design (visual, UX, product design)
Use design language: deliverables, screens, components, design systems, prototypes, wireframes, specs, stakeholders, design reviews.
"""

UXR_DOMAIN = """Domain: UX Research
Use research language: synthesis, coding, themes, evidence chains, transcripts, participants, findings, readouts, codebooks, verification against source material.
"""

SYSTEM_PROMPT = """\
You are an expert in assessment design, specifically Guttman-type cumulative scales \
and contrastive anchoring for self-assessment instruments. You write clear, natural \
questions that sound like a thoughtful colleague asking about your practice — never \
formulaic or academic. You always return valid JSON with no surrounding commentary."""


def build_prompt(sae_level: int, track: str) -> str:
    """Build the generation prompt for one SAE level."""
    level_info = SAE_LEVELS[sae_level]
    domain = DESIGN_DOMAIN if track == "design" else UXR_DOMAIN

    return textwrap.dedent(f"""\
    I need you to write 5 EPIAS questions for SAE Level {sae_level} ({level_info['name']}) in the {track.upper()} track.

    ## Framework Context

    The EPIAS scale measures HOW MATURE someone's practice is — from individual experimentation to organizational leadership. It's orthogonal to SAE level (which measures automation). A person can be at any EPIAS stage at any SAE level.

    **EPIAS Stages (each builds on the previous):**
    - E (Explorer): {EPIAS_STAGES['E']}
    - P (Practitioner): {EPIAS_STAGES['P']}
    - I (Integrator): {EPIAS_STAGES['I']}
    - A (Architect): {EPIAS_STAGES['A']}
    - S (Steward): {EPIAS_STAGES['S']}

    **SAE Level {sae_level}: {level_info['name']}**
    {level_info['desc']}

    **What EPIAS measures at this level:** {level_info['epias_focus']}

    {domain}

    ## Style Examples
    {SAE_EXEMPLARS}

    ## Critical Rules

    1. **MUTUAL EXCLUSIVITY**: Each option must contain a self-limiting clause that makes it feel wrong for someone at a higher stage. The E option should feel too narrow for a Practitioner. The P option should feel too narrow for an Integrator. And so on.

    2. **Self-limiting patterns**:
       - E options should include phrases like "still figuring out", "inconsistent", "haven't found reliable patterns"
       - P options should include "but it's personal / in my head / only I use it / others haven't adopted it"
       - I options should include "documented", "traceable", "others can review"
       - A options should include "others use my systems without my help"
       - S options should include "I set standards for the organization", "I mentor", "I govern"

    3. **Natural stems**: Each question stem should be a natural, specific question about a concrete dimension — not a formulaic pattern. Vary the stem structure. Some can start with "How...", some with "What...", some with "When...". They should sound like something a thoughtful colleague would ask.

    4. **Plain language**: No jargon. One sentence per option, max two short clauses joined by an em dash.

    5. **Concrete behaviors**: Options describe what someone DOES, not what they believe or aspire to.

    6. **Five dimensions**: Choose 5 distinct dimensions relevant to SAE Level {sae_level}. Each dimension should measure a different facet of maturity at this level of AI use.

    ## Output Format

    Return ONLY a JSON array of 5 question objects. No markdown fences, no commentary.

    [
      {{
        "id": "epias_l{sae_level}_<dimension_slug>",
        "dimension": "<dimension_name>",
        "question": "<natural question stem>",
        "options": [
          {{"stage": "E", "text": "<explorer option with self-limiting clause>"}},
          {{"stage": "P", "text": "<practitioner option with self-limiting clause>"}},
          {{"stage": "I", "text": "<integrator option>"}},
          {{"stage": "A", "text": "<architect option>"}},
          {{"stage": "S", "text": "<steward option>"}}
        ]
      }}
    ]
    """)


def generate_level(client: OpenAI, sae_level: int, track: str) -> list:
    """Call GPT-5.2 to generate EPIAS questions for one SAE level + track."""
    prompt = build_prompt(sae_level, track)

    resp = client.responses.create(
        model="gpt-5.2",
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
        max_output_tokens=4096,
        reasoning={"effort": "high"},
    )

    # Extract text from response
    text = ""
    if hasattr(resp, "output_text") and resp.output_text:
        text = resp.output_text.strip()
    elif hasattr(resp, "output") and resp.output:
        for block in resp.output:
            if hasattr(block, "content"):
                for item in block.content:
                    if hasattr(item, "text"):
                        text = item.text.strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Generate EPIAS questions via GPT-5.2")
    parser.add_argument("--level", type=int, choices=range(6), default=None,
                        help="Generate for a single SAE level (0-5). Default: all.")
    parser.add_argument("--track", choices=["design", "uxr", "both"], default="both",
                        help="Which track to generate. Default: both.")
    parser.add_argument("--output", type=str, default="scripts/epias_generated.json",
                        help="Output file path (relative to assessment/)")
    args = parser.parse_args()

    client = OpenAI()

    levels = [args.level] if args.level is not None else list(range(6))
    tracks = ["design", "uxr"] if args.track == "both" else [args.track]

    results = {}

    for track in tracks:
        track_key = f"EPIAS_QUESTIONS_{track.upper()}"
        results[track_key] = {}

        for level in levels:
            label = f"{track.upper()} L{level}"
            print(f"Generating {label}...", file=sys.stderr)

            questions = generate_level(client, level, track)
            results[track_key][level] = questions

            print(f"  ✓ {label}: {len(questions)} questions", file=sys.stderr)

            # Show stems for quick review
            for q in questions:
                print(f"    • {q['question']}", file=sys.stderr)

    # Save to file
    out_path = Path(__file__).parent.parent / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to {out_path}", file=sys.stderr)

    # Also print to stdout for piping
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

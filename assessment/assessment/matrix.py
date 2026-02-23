"""EPIAS x SAE matrix data and growth path recommendations."""

# Cell descriptions: (sae_level, epias_stage) -> description
# Extracted from the DIT 2026 framework
MATRIX_DATA = {
    # SAE L0: Manual
    (0, "E"): "Exploring fundamentals; inconsistent results, still learning.",
    (0, "P"): "Consistent manual practice with repeatable techniques.",
    (0, "I"): "Manual workflow with validation, traceability, and documented decisions.",
    (0, "A"): "Reusable templates and processes the team adopts.",
    (0, "S"): "Organizational standards for craft quality; mentors others.",

    # SAE L1: AI-Assisted
    (1, "E"): "Trying AI for ideas and drafts; hit-or-miss, heavily rewritten.",
    (1, "P"): "Using AI daily with saved prompts and basic quality checks.",
    (1, "I"): "AI embedded across full tasks with sources noted and decisions explained.",
    (1, "A"): "Shared prompt libraries and review checklists teammates reuse.",
    (1, "S"): "Team standards for AI-assisted work; governs usage and review.",

    # SAE L2: Partially Automated
    (2, "E"): "Trying app-builders to generate screens; lots of rework needed.",
    (2, "P"): "Repeatable components from clear specs with a done checklist.",
    (2, "I"): "Outputs fit known patterns; prompts are traceable end-to-end.",
    (2, "A"): "Reusable generators teammates run for consistent results.",
    (2, "S"): "Team norms for what to automate; governs review expectations.",

    # SAE L3: Guided Automation
    (3, "E"): "Moving into IDE workflows; multi-step runs are inconsistent.",
    (3, "P"): "Reliable multi-step workflows with checkpoints and lightweight evals.",
    (3, "I"): "Clear framing: what AI executes, what humans approve, when to intervene.",
    (3, "A"): "Shared workflows, context libraries, and eval templates teammates run.",
    (3, "S"): "Org standards for IDE-based AI work; maintains shared tools.",

    # SAE L4: Mostly Automated
    (4, "E"): "Experimenting with agent pipelines; results need heavy validation.",
    (4, "P"): "Harnesses with repeatable execution, evals, retries, and escalation.",
    (4, "I"): "End-to-end autonomous workflows with comprehensive eval suites.",
    (4, "A"): "Production-grade agent infrastructure others operate.",
    (4, "S"): "Governance for autonomous systems at scale; org-level eval infrastructure.",

    # SAE L5: Full Automation
    (5, "E"): "Exploring goal-setting for autonomous AI; exception handling unclear.",
    (5, "P"): "Consistent approval gates and routine review of autonomous outputs.",
    (5, "I"): "Autonomous workflows with documented exception handling and escalation.",
    (5, "A"): "Goal-setting and approval systems others trust; reusable governance.",
    (5, "S"): "Enterprise governance for fully autonomous AI; org-wide trust standards.",
}


# Growth paths: (sae_level, epias_stage) -> next step recommendations
GROWTH_PATHS = {
    # L0
    (0, "E"): {
        "next": {"sae_level": 0, "epias_stage": "P"},
        "signal": "I have consistent techniques I can rely on.",
        "actions": ["Develop repeatable manual processes", "Document what works", "Build consistency in output quality"],
    },
    (0, "P"): {
        "next": {"sae_level": 0, "epias_stage": "I"},
        "signal": "My work is traceable and well-documented.",
        "actions": ["Add validation steps to your workflow", "Document design decisions with rationale", "Create traceability from requirements to outputs"],
    },
    (0, "I"): {
        "next": {"sae_level": 0, "epias_stage": "A"},
        "signal": "Others adopt my processes and templates.",
        "actions": ["Turn your personal systems into reusable templates", "Create onboarding materials for your processes", "Build shared resources others can use"],
    },
    (0, "A"): {
        "next": {"sae_level": 0, "epias_stage": "S"},
        "signal": "I set the standard for design quality here.",
        "actions": ["Establish organizational design standards", "Mentor others in craft techniques", "Maintain and evolve shared design systems"],
    },
    (0, "S"): {
        "next": {"sae_level": 1, "epias_stage": "E"},
        "signal": "I'm ready to explore how AI can augment my strong manual foundation.",
        "actions": ["Start experimenting with ChatGPT or Claude for brainstorming", "Try AI for one specific task you do repeatedly", "Maintain your judgment while exploring AI assistance"],
    },

    # L1
    (1, "E"): {
        "next": {"sae_level": 1, "epias_stage": "P"},
        "signal": "I know when AI will help before I ask it.",
        "actions": ["Reuse AI for the same task type", "Save prompts that work", "Add light structure: context \u2192 task \u2192 output"],
    },
    (1, "P"): {
        "next": {"sae_level": 1, "epias_stage": "I"},
        "signal": "I can clearly explain what AI contributed \u2014 and what I decided.",
        "actions": ["Use AI across multiple steps (research \u2192 draft \u2192 refine)", "Note where AI was used and reviewed", "Explain why outputs were accepted or rejected"],
    },
    (1, "I"): {
        "next": {"sae_level": 1, "epias_stage": "A"},
        "signal": "Others can use my prompts and get similar-quality results.",
        "actions": ["Turn prompts into reusable patterns", "Create review habits around AI output", "Build prompt libraries organized by task"],
    },
    (1, "A"): {
        "next": {"sae_level": 1, "epias_stage": "S"},
        "signal": "AI use is trusted here because expectations are clear.",
        "actions": ["Set clear guidance on acceptable AI use", "Establish review norms for AI-assisted work", "Coach others on judgment and accountability"],
    },
    (1, "S"): {
        "next": {"sae_level": 2, "epias_stage": "E"},
        "signal": "I'm ready to ask AI to build, not just think.",
        "actions": ["Identify safe-to-automate chunks", "Try app-builders (Bolt, Lovable, v0) for bounded components", "Carry your L1 judgment into L2 exploration"],
    },

    # L2
    (2, "E"): {
        "next": {"sae_level": 2, "epias_stage": "P"},
        "signal": "I can reliably generate this kind of component with predictable quality.",
        "actions": ["Write explicit instructions, not vibes", "Define 'done' for a generated component", "Use the same prompt more than once"],
    },
    (2, "P"): {
        "next": {"sae_level": 2, "epias_stage": "I"},
        "signal": "I can explain why this output is trustworthy.",
        "actions": ["Break work into bounded chunks on purpose", "Add manual QA checklists (a11y, hierarchy, tone)", "Document what AI was asked vs what it produced"],
    },
    (2, "I"): {
        "next": {"sae_level": 2, "epias_stage": "A"},
        "signal": "People ask to use my AI workflows.",
        "actions": ["Turn good prompts into reusable templates", "Decide which chunks are worth automating", "Design guardrails, not just prompts"],
    },
    (2, "A"): {
        "next": {"sae_level": 2, "epias_stage": "S"},
        "signal": "The team trusts the automation boundaries I've set.",
        "actions": ["Set standards for partial automation", "Govern when automation helps vs hurts", "Mentor on safe integration"],
    },
    (2, "S"): {
        "next": {"sae_level": 3, "epias_stage": "E"},
        "signal": "I'm ready to think in runs, not screens.",
        "actions": ["Move from chat to IDE-based workflows", "Learn basic context engineering", "Start with multi-step runs: plan \u2192 generate \u2192 review"],
    },

    # L3
    (3, "E"): {
        "next": {"sae_level": 3, "epias_stage": "P"},
        "signal": "My workflows don't fall apart every other run.",
        "actions": ["Create a standard run template (same steps every time)", "Add 'stop and review' gates at predictable points", "Use system prompts and instruction blocks consistently"],
    },
    (3, "P"): {
        "next": {"sae_level": 3, "epias_stage": "I"},
        "signal": "I trust this workflow until it triggers a known exception.",
        "actions": ["Define clear ownership: AI generates, human approves", "Add simple eval checks (structure, length, criteria)", "Document failure modes and fixes"],
    },
    (3, "I"): {
        "next": {"sae_level": 3, "epias_stage": "A"},
        "signal": "My system runs even when I'm not there to coach.",
        "actions": ["Build modular context (inputs, rules, examples separated)", "Create reusable Skills or agent tasks", "Develop shared eval patterns"],
    },
    (3, "A"): {
        "next": {"sae_level": 3, "epias_stage": "S"},
        "signal": "People trust IDE-agent work because expectations are explicit.",
        "actions": ["Set standards for IDE + AI usage", "Mentor on context engineering", "Maintain shared Skills, MCP tools, and workflow libraries"],
    },
    (3, "S"): {
        "next": {"sae_level": 4, "epias_stage": "E"},
        "signal": "I'm ready for the harness to become the workspace.",
        "actions": ["Extract your best L3 workflow into a runnable spec", "Add eval gates that decide pass/retry/escalate", "Implement automatic retries with corrective prompts"],
    },

    # L4
    (4, "E"): {
        "next": {"sae_level": 4, "epias_stage": "P"},
        "signal": "My harness runs reliably with consistent patterns.",
        "actions": ["Establish repeatable execution patterns", "Add evals, retries, and escalation paths", "Build logging and auditability"],
    },
    (4, "P"): {
        "next": {"sae_level": 4, "epias_stage": "I"},
        "signal": "My system self-heals for known exception classes.",
        "actions": ["Add comprehensive eval suites (structure, quality, regression)", "Document exception classes and recovery paths", "Implement automatic retry with corrective prompts"],
    },
    (4, "I"): {
        "next": {"sae_level": 4, "epias_stage": "A"},
        "signal": "Others operate my infrastructure and trust the results.",
        "actions": ["Make your harness operable by others", "Add documentation and onboarding", "Build shared skill libraries and eval pipelines"],
    },
    (4, "A"): {
        "next": {"sae_level": 4, "epias_stage": "S"},
        "signal": "I govern autonomous systems at organizational scale.",
        "actions": ["Define risk thresholds and approval gates", "Establish accountability frameworks", "Maintain org-level eval and autonomy infrastructure"],
    },
    (4, "S"): {
        "next": {"sae_level": 5, "epias_stage": "E"},
        "signal": "I'm ready to explore full autonomy (when it becomes possible).",
        "actions": ["Explore goal-setting interfaces for autonomous AI", "Define exception handling for fully autonomous systems", "SAE L5 is aspirational \u2014 focus on deepening L4 mastery"],
    },

    # L5
    (5, "E"): {
        "next": {"sae_level": 5, "epias_stage": "P"},
        "signal": "I consistently set quality bars for autonomous systems.",
        "actions": ["Set approval gates and quality bars", "Establish routine review of autonomous outputs", "Build exception handling clarity"],
    },
    (5, "P"): {
        "next": {"sae_level": 5, "epias_stage": "I"},
        "signal": "Autonomous workflows are validated with clear escalation.",
        "actions": ["Document exception handling systems", "Create clear escalation paths", "Validate autonomous workflows end-to-end"],
    },
    (5, "I"): {
        "next": {"sae_level": 5, "epias_stage": "A"},
        "signal": "Others trust my governance frameworks.",
        "actions": ["Design goal-setting and approval systems", "Create reusable governance frameworks", "Build trust calibration tools"],
    },
    (5, "A"): {
        "next": {"sae_level": 5, "epias_stage": "S"},
        "signal": "I set enterprise AI governance standards.",
        "actions": ["Define organizational AI risk and trust standards", "Create enterprise approval frameworks", "Establish cross-team accountability"],
    },
    (5, "S"): {
        "next": None,
        "signal": "You've reached the theoretical peak. Stay curious and keep evolving.",
        "actions": ["Maintain and evolve organizational AI governance", "Push the boundaries of what's possible", "Remember: SAE L5 is still aspirational"],
    },
}


# Key insight from the framework
KEY_INSIGHT = (
    "An S-Steward at L1 is more valuable than an E-Explorer at L4. "
    "Depth of judgment beats breadth of tooling."
)


def get_placement(score: dict) -> dict:
    """Get matrix cell description + growth path for a scored assessment."""
    key = (score["sae_level"], score["epias_stage"])
    growth = GROWTH_PATHS.get(key, {})

    return {
        **score,
        "cell_description": MATRIX_DATA.get(key, ""),
        "growth_path": growth,
        "key_insight": KEY_INSIGHT,
    }


def get_full_matrix() -> dict:
    """Return full matrix data for visualization."""
    cells = {}
    for (level, stage), desc in MATRIX_DATA.items():
        cells[f"{level}_{stage}"] = desc

    return {
        "levels": list(range(6)),
        "level_names": {str(k): v for k, v in {0: "L0: Classical Designer", 1: "L1: Marketing Designer \u00d7 AI", 2: "L2: Product Designer \u00d7 AI", 3: "L3: Design Engineer \u00d7 AI", 4: "L4: Super Design Engineer \u00d7 AI", 5: "L5: AI \u00d7 AI"}.items()},
        "stages": ["E", "P", "I", "A", "S"],
        "stage_names": {"E": "Explorer", "P": "Practitioner", "I": "Integrator", "A": "Architect", "S": "Steward"},
        "cells": cells,
    }

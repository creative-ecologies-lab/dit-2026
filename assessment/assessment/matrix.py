"""EPIAS x SAE matrix data and growth path recommendations."""
from assessment.scorer import SAE_NAMES, STAGE_NAMES

# Cell descriptions: (sae_level, epias_stage) -> description
# Adapted from John Maeda's DIT 2026 framework tables
MATRIX_DATA = {
    # SAE L0: Manual — Classical Designer (no AI)
    (0, "E"): "Explores craft fundamentals — learning manual techniques with inconsistent results. Quality varies and guidance is needed.",
    (0, "P"): "Has consistent manual practice with developed habits and repeatable techniques. Process is reliable with quality checks in place.",
    (0, "I"): "Maintains a fully integrated manual workflow with validation steps, traceability, and clear decision documentation. Can explain every choice made.",
    (0, "A"): "Builds reusable manual systems, templates, and processes that others adopt. Design systems are clear enough for engineers and PMs to make basic decisions independently.",
    (0, "S"): "Sets organizational standards for craft quality. Mentors others in manual techniques and maintains shared design systems.",

    # SAE L1: AI-Assisted — Marketing Designer × AI
    (1, "E"): "Tries AI chat tools and generators for ideas and drafts. Outputs are hit-or-miss and heavily rewritten. Still figuring out when AI actually helps.",
    (1, "P"): "Uses AI daily with saved prompts, consistent structure and tone, and basic quality checks before using outputs. Knows when AI will help before asking.",
    (1, "I"): "Embeds AI across full tasks — research, ideation, drafting, refining — with sources noted, decisions explained, and manual validation at each step.",
    (1, "A"): "Builds shared prompt libraries, review checklists, and example outputs that teammates reuse and trust. Others get design-quality drafts from these systems.",
    (1, "S"): "Sets team standards for AI-assisted work — what's allowed, how it's reviewed. Mentors others on prompting and judgment, and governs usage across the org.",

    # SAE L2: Partially Automated — Product Designer × AI
    (2, "E"): "Tries app-builders and component generators to create screens and components. Lots of manual stitching and rework, but learning what works.",
    (2, "P"): "Gets repeatable components from clear specs, using a 'definition of done' checklist before integrating. Spends more time integrating than fixing.",
    (2, "I"): "Produces outputs that fit known integration patterns — tokens, layout, accessibility. Prompts and inputs are traceable from request to result to final output.",
    (2, "A"): "Builds reusable component templates and prompt packs that teammates run with consistent results. Non-designers can generate on-brand UI that passes review.",
    (2, "S"): "Sets team norms for what's safe to automate at L2 and what isn't. Mentors others on integration and QA, and governs usage and review expectations.",

    # SAE L3: Guided Automation — Design Engineer × AI
    (3, "E"): "Moves work into an AI-enabled IDE and learns context rules. Multi-step runs are inconsistent and fragile, but crossing the threshold into shipping real PRs.",
    (3, "P"): "Runs reliable multi-step workflows inside the IDE with explicit checkpoints — plan, generate, review, revise. Lightweight evals run by default.",
    (3, "I"): "Has clear decision framing for IDE-run workflows: what AI executes, what humans approve, and when to intervene. Failure modes are documented.",
    (3, "A"): "Builds shared IDE workflows — reusable skills, context libraries, and eval templates that teammates run. Creates starter codebases for PMs and designers to experiment with.",
    (3, "S"): "Sets org standards for IDE-based AI work — safety, quality, traceability. Mentors on context engineering and maintains the shared tools everyone depends on.",

    # SAE L4: Mostly Automated — Super Design Engineer × AI
    (4, "E"): "Experiments with autonomous harnesses and agent pipelines. Results require heavy validation and manual debugging. Learning what 'trust the system' means.",
    (4, "P"): "Maintains harnesses with repeatable execution patterns — evals, retries, and escalation paths consistently applied. Work can complete unattended.",
    (4, "I"): "Runs end-to-end workflows autonomously with comprehensive eval suites validating outputs. Exception classes and recovery paths are documented.",
    (4, "A"): "Builds production-grade agent infrastructure others operate — self-improving harnesses, shared skill libraries, and eval-driven pipelines. PMs and designers trigger workflows without opening a terminal.",
    (4, "S"): "Governs autonomous systems at scale — defining risk thresholds, approval gates, and accountability. Maintains org-level eval and autonomy infrastructure.",

    # SAE L5: Full Automation — AI × AI (aspirational)
    (5, "E"): "Explores goal-setting interfaces for autonomous AI. Exception handling is still unclear. Frontier territory — L5 is aspirational, not yet real.",
    (5, "P"): "Sets approval gates and quality bars consistently, with routine review of autonomous outputs. Building the habits for a world that's still arriving.",
    (5, "I"): "Validates autonomous workflows with exception handling systems and clear escalation paths. Trusts the system unless it alerts.",
    (5, "A"): "Designs goal-setting and approval systems that others trust — reusable governance frameworks where cross-functional teams set AI goals together.",
    (5, "S"): "Establishes enterprise governance for fully autonomous AI. Sets organizational risk and trust standards, approval frameworks, and cross-team accountability.",
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

    # Role labels per SAE level (from DIT 2026 framework)
    role_labels = {
        0: "Classical Designer", 1: "Marketing Designer \u00d7 AI",
        2: "Product Designer \u00d7 AI", 3: "Design Engineer \u00d7 AI",
        4: "Super Design Engineer \u00d7 AI", 5: "AI \u00d7 AI",
    }

    return {
        "levels": list(range(6)),
        "level_names": {str(k): f"L{k}: {role_labels[k]}" for k in range(6)},
        "stages": list(STAGE_NAMES.keys()),
        "stage_names": dict(STAGE_NAMES),
        "cells": cells,
    }

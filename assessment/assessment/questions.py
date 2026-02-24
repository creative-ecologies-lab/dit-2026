"""Self-assessment questionnaire definitions for E-P-I-A-S x SAE Framework."""

SAE_QUESTIONS = [
    {
        "id": "sae_tools",
        "question": "Which best describes the AI tools in your workflow?",
        "options": [
            {"level": 0, "text": "I don't use AI tools \u2014 all my work is manual."},
            {"level": 1, "text": "I use ChatGPT or Midjourney for ideas and drafts, but I direct every step."},
            {"level": 2, "text": "I use AI tools to generate deliverables (documents, screens, code) from specs."},
            {"level": 3, "text": "I work in an IDE with multi-step AI workflows, checkpoints, and context engineering."},
            {"level": 4, "text": "I run automated agent harnesses with eval suites that execute autonomously."},
            {"level": 5, "text": "AI runs most of my workflow \u2014 I set goals and review exceptions."},
        ]
    },
    {
        "id": "sae_qa",
        "question": "How do you quality-check AI outputs?",
        "options": [
            {"level": 0, "text": "N/A \u2014 I don't use AI in my work."},
            {"level": 1, "text": "I manually review and heavily rewrite everything AI produces."},
            {"level": 2, "text": "I run a checklist (consistency, quality standards, tone) before integrating AI output."},
            {"level": 3, "text": "I have lightweight evals and explicit review gates in my workflows."},
            {"level": 4, "text": "Automated eval suites decide pass, retry, or escalate without my input."},
            {"level": 5, "text": "Self-correcting systems handle QA \u2014 I only review flagged exceptions."},
        ]
    },
    {
        "id": "sae_laptop",
        "question": "What happens when you close your laptop?",
        "options": [
            {"level": 0, "text": "N/A \u2014 I don't use AI, so nothing changes."},
            {"level": 1, "text": "Everything pauses \u2014 AI only works when I'm actively prompting."},
            {"level": 2, "text": "Everything pauses \u2014 I manually assemble AI-generated pieces when I return."},
            {"level": 3, "text": "Everything pauses \u2014 my workflows need me to review and approve."},
            {"level": 4, "text": "Work continues \u2014 my harnesses run, evaluate, and retry on their own."},
            {"level": 5, "text": "Work continues indefinitely \u2014 I only review flagged exceptions."},
        ]
    },
    {
        "id": "sae_prompting",
        "question": "How do you instruct AI?",
        "options": [
            {"level": 0, "text": "I don't write prompts for AI."},
            {"level": 1, "text": "I write ad-hoc prompts and iterate until the output looks right."},
            {"level": 2, "text": "I write structured prompts with context, constraints, and output format."},
            {"level": 3, "text": "I engineer context blocks (system prompts, rules, examples) for multi-step workflows."},
            {"level": 4, "text": "I build harness configs with eval gates, retry logic, and corrective prompts."},
            {"level": 5, "text": "I set high-level goals \u2014 the system manages its own prompting."},
        ]
    },
    {
        "id": "sae_outputs",
        "question": "What kind of work artifacts does AI help you produce?",
        "options": [
            {"level": 0, "text": "None \u2014 I produce everything manually."},
            {"level": 1, "text": "Ideas, copy drafts, and concepts that I heavily refine."},
            {"level": 2, "text": "Usable outputs (screens, documents, code) from clear specs."},
            {"level": 3, "text": "Large features via orchestrated multi-step workflows with human QA checkpoints."},
            {"level": 4, "text": "End-to-end features that are generated, tested, and QA'd automatically."},
            {"level": 5, "text": "Complete products with autonomous iteration and self-correction."},
        ]
    },
    {
        "id": "sae_reuse",
        "question": "How reusable are your AI workflows?",
        "options": [
            {"level": 0, "text": "N/A \u2014 I don't use AI workflows."},
            {"level": 1, "text": "I save some prompts and reuse them occasionally."},
            {"level": 2, "text": "I have reusable prompt templates with context and constraints sections."},
            {"level": 3, "text": "I maintain shared workflow scripts and context libraries."},
            {"level": 4, "text": "I maintain production-grade agent infrastructure others operate."},
            {"level": 5, "text": "Self-improving harnesses that evolve with usage data."},
        ]
    },
]


# Stage 2: EPIAS Maturity questions (5 per SAE level, testing E/P/I/A/S)
# Generated dynamically based on the identified SAE level
EPIAS_QUESTIONS = {
    0: [
        {
            "id": "epias_l0_craft",
            "dimension": "craft_maturity",
            "question": "How would you describe your manual craft and practice?",
            "options": [
                {"stage": "E", "text": "I'm exploring fundamentals \u2014 my quality varies and I need guidance."},
                {"stage": "P", "text": "I have consistent practice with repeatable techniques and habits."},
                {"stage": "I", "text": "My workflow includes validation steps and clear decision documentation."},
                {"stage": "A", "text": "I've built reusable templates and processes that my team adopts."},
                {"stage": "S", "text": "I set organizational standards for craft quality and mentor others."},
            ]
        },
        {
            "id": "epias_l0_consistency",
            "dimension": "consistency",
            "question": "How consistent is the quality of your design outputs?",
            "options": [
                {"stage": "E", "text": "Inconsistent \u2014 some work is great, some needs heavy revision."},
                {"stage": "P", "text": "Reliably good \u2014 I follow a process that keeps quality steady."},
                {"stage": "I", "text": "Consistently high with documented rationale for every decision."},
                {"stage": "A", "text": "Others using my templates achieve similar quality independently."},
                {"stage": "S", "text": "I define and maintain quality standards for the organization."},
            ]
        },
        {
            "id": "epias_l0_documentation",
            "dimension": "documentation",
            "question": "How do you document your design decisions?",
            "options": [
                {"stage": "E", "text": "Rarely \u2014 decisions live in my head."},
                {"stage": "P", "text": "I keep notes on what worked for my own reference."},
                {"stage": "I", "text": "I document decisions with rationale so they're traceable and reviewable."},
                {"stage": "A", "text": "I've created documentation frameworks others use for their decisions."},
                {"stage": "S", "text": "I maintain organizational standards for design documentation."},
            ]
        },
        {
            "id": "epias_l0_sharing",
            "dimension": "knowledge_sharing",
            "question": "How do you share your design knowledge?",
            "options": [
                {"stage": "E", "text": "I mostly learn from others and haven't started sharing."},
                {"stage": "P", "text": "I share tips and techniques informally with teammates."},
                {"stage": "I", "text": "I contribute to team knowledge bases and design reviews."},
                {"stage": "A", "text": "I've built reusable assets (templates, systems) others rely on."},
                {"stage": "S", "text": "I run training, set standards, and mentor across the organization."},
            ]
        },
        {
            "id": "epias_l0_process",
            "dimension": "process_maturity",
            "question": "How structured is your design process?",
            "options": [
                {"stage": "E", "text": "Mostly ad-hoc \u2014 I figure it out as I go."},
                {"stage": "P", "text": "I follow a repeatable process with defined steps."},
                {"stage": "I", "text": "My process is integrated end-to-end with product development."},
                {"stage": "A", "text": "I've designed processes that entire teams follow."},
                {"stage": "S", "text": "I maintain and evolve organizational design processes."},
            ]
        },
    ],
    1: [
        {
            "id": "epias_l1_consistency",
            "dimension": "output_consistency",
            "question": "How consistent are your AI-assisted design outputs?",
            "options": [
                {"stage": "E", "text": "Hit-or-miss \u2014 I try things and see what happens."},
                {"stage": "P", "text": "Predictable \u2014 I know what to expect from my saved prompts."},
                {"stage": "I", "text": "Reliable across full tasks: research \u2192 ideation \u2192 draft \u2192 refine."},
                {"stage": "A", "text": "Others reuse my prompt libraries and get similar-quality results."},
                {"stage": "S", "text": "I set the quality standard for AI-assisted work that the team follows."},
            ]
        },
        {
            "id": "epias_l1_judgment",
            "dimension": "ai_judgment",
            "question": "How well do you know when AI helps versus hurts?",
            "options": [
                {"stage": "E", "text": "Still figuring out what AI is good at versus poor at."},
                {"stage": "P", "text": "I know when AI will help before I ask it."},
                {"stage": "I", "text": "I can clearly explain what AI contributed versus what I decided."},
                {"stage": "A", "text": "I've documented AI usage guidelines for the team."},
                {"stage": "S", "text": "I set organizational policy on acceptable AI use."},
            ]
        },
        {
            "id": "epias_l1_prompts",
            "dimension": "prompt_maturity",
            "question": "How do you manage your prompts?",
            "options": [
                {"stage": "E", "text": "I write new prompts each time \u2014 nothing is saved."},
                {"stage": "P", "text": "I save and reuse structured prompts (context \u2192 task \u2192 output)."},
                {"stage": "I", "text": "I use prompts intentionally across multi-step tasks with sources noted."},
                {"stage": "A", "text": "I maintain prompt libraries organized by task type with review checklists."},
                {"stage": "S", "text": "I govern prompt standards and train others on prompting judgment."},
            ]
        },
        {
            "id": "epias_l1_accountability",
            "dimension": "accountability",
            "question": "How do you handle accountability for AI-generated work?",
            "options": [
                {"stage": "E", "text": "I don't think much about it \u2014 I use what looks good."},
                {"stage": "P", "text": "I always manually verify before using AI output."},
                {"stage": "I", "text": "I note where AI was used and why outputs were accepted or rejected."},
                {"stage": "A", "text": "I've created example libraries showing good versus risky AI outputs."},
                {"stage": "S", "text": "I set review norms and governance for AI-assisted work."},
            ]
        },
        {
            "id": "epias_l1_teaching",
            "dimension": "knowledge_transfer",
            "question": "How do you help others learn to use AI in design?",
            "options": [
                {"stage": "E", "text": "I'm still learning myself."},
                {"stage": "P", "text": "I share tips and tricks that work for me."},
                {"stage": "I", "text": "I demonstrate full AI-assisted workflows with clear rationale."},
                {"stage": "A", "text": "Others routinely ask to use my AI workflows and libraries."},
                {"stage": "S", "text": "I mentor others on AI judgment and maintain shared systems."},
            ]
        },
    ],
    2: [
        {
            "id": "epias_l2_specs",
            "dimension": "specification_quality",
            "question": "How clear are the specs you give AI generation tools?",
            "options": [
                {"stage": "E", "text": "Vague \u2014 lots of manual stitching and rework needed."},
                {"stage": "P", "text": "Clear enough for repeatable components with a definition-of-done checklist."},
                {"stage": "I", "text": "Outputs fit known patterns (tokens, layout, a11y) and prompts are traceable."},
                {"stage": "A", "text": "I've created reusable component generators teammates run consistently."},
                {"stage": "S", "text": "I set team norms for what to automate and how to review generated output."},
            ]
        },
        {
            "id": "epias_l2_integration",
            "dimension": "integration",
            "question": "How do you integrate AI-generated components?",
            "options": [
                {"stage": "E", "text": "Copy-paste and heavily modify by hand."},
                {"stage": "P", "text": "I check consistency, quality standards, and tone before integrating."},
                {"stage": "I", "text": "I have repeatable integration patterns with explicit handoff notes."},
                {"stage": "A", "text": "I've built generate-check-refine bundles others use."},
                {"stage": "S", "text": "I govern which chunks are safe to automate and set review expectations."},
            ]
        },
        {
            "id": "epias_l2_chunking",
            "dimension": "work_decomposition",
            "question": "How do you decide what to ask AI to build?",
            "options": [
                {"stage": "E", "text": "I try generating whole pages and see what comes out."},
                {"stage": "P", "text": "I know which bounded units (buttons, forms, cards) AI handles well."},
                {"stage": "I", "text": "I break work into safe-to-automate chunks with clear inputs and done criteria."},
                {"stage": "A", "text": "I've created component-specific generators for common patterns."},
                {"stage": "S", "text": "I decide which work types the team automates versus does manually."},
            ]
        },
        {
            "id": "epias_l2_quality",
            "dimension": "quality_assurance",
            "question": "How do you ensure quality of AI-generated output?",
            "options": [
                {"stage": "E", "text": "Visual inspection and gut feel."},
                {"stage": "P", "text": "A checklist: consistency, quality standards, tone."},
                {"stage": "I", "text": "Documented QA process with traceability from request to final."},
                {"stage": "A", "text": "Shared QA bundles with prompt templates for consistent review."},
                {"stage": "S", "text": "I set and maintain review standards for all AI-generated UI."},
            ]
        },
        {
            "id": "epias_l2_reuse",
            "dimension": "reusability",
            "question": "How reusable are your AI generation workflows?",
            "options": [
                {"stage": "E", "text": "I start fresh each time with new prompts."},
                {"stage": "P", "text": "I reuse prompt templates and expect similar quality each run."},
                {"stage": "I", "text": "I maintain prompt libraries organized by component type."},
                {"stage": "A", "text": "Others rely on my shared libraries for generation."},
                {"stage": "S", "text": "I maintain and govern team-wide generation standards."},
            ]
        },
    ],
    3: [
        {
            "id": "epias_l3_reliability",
            "dimension": "workflow_reliability",
            "question": "How reliable are your multi-step AI workflows?",
            "options": [
                {"stage": "E", "text": "Inconsistent and fragile \u2014 multi-step runs break often."},
                {"stage": "P", "text": "Reliable with checkpoints: plan \u2192 generate \u2192 review \u2192 revise."},
                {"stage": "I", "text": "Clear framing: what AI executes, what humans approve, when to intervene."},
                {"stage": "A", "text": "Others run my workflows and get comparable quality without coaching."},
                {"stage": "S", "text": "I set org standards for IDE-based AI work (safety, quality, traceability)."},
            ]
        },
        {
            "id": "epias_l3_context",
            "dimension": "context_engineering",
            "question": "How sophisticated is your context engineering?",
            "options": [
                {"stage": "E", "text": "Learning basic context rules \u2014 mostly trial and error."},
                {"stage": "P", "text": "I use system prompts, instruction blocks, and explicit review moments."},
                {"stage": "I", "text": "I have lightweight evals and documented failure modes."},
                {"stage": "A", "text": "I maintain modular context libraries (brand voice, design system, constraints)."},
                {"stage": "S", "text": "I mentor others on context engineering and maintain shared tools."},
            ]
        },
        {
            "id": "epias_l3_failures",
            "dimension": "failure_handling",
            "question": "How do you handle workflow failures?",
            "options": [
                {"stage": "E", "text": "I start over or try different prompts until something works."},
                {"stage": "P", "text": "I have retry patterns and know the common failure modes."},
                {"stage": "I", "text": "I've documented failure taxonomy and escalation triggers."},
                {"stage": "A", "text": "My workflows have built-in exception handling teammates understand."},
                {"stage": "S", "text": "I define organizational standards for failure handling and risk."},
            ]
        },
        {
            "id": "epias_l3_tooling",
            "dimension": "tooling",
            "question": "What kind of IDE/AI tooling do you use?",
            "options": [
                {"stage": "E", "text": "Basic IDE with a copilot \u2014 still learning to use it effectively."},
                {"stage": "P", "text": "IDE with MCP tools and a stable run-loop template."},
                {"stage": "I", "text": "IDE with structured evals, approval gates, and ownership boundaries."},
                {"stage": "A", "text": "Reusable workflow scripts and context libraries teams can invoke."},
                {"stage": "S", "text": "I maintain shared IDE/AI infrastructure and govern tool access."},
            ]
        },
        {
            "id": "epias_l3_ownership",
            "dimension": "decision_ownership",
            "question": "How clear is the division of work between you and AI?",
            "options": [
                {"stage": "E", "text": "Blurry \u2014 I'm not always sure what AI decided versus what I decided."},
                {"stage": "P", "text": "Clear \u2014 I know my checkpoints and what I'm responsible for."},
                {"stage": "I", "text": "Explicitly defined: AI generates, human approves, with documented handoffs."},
                {"stage": "A", "text": "My team follows the same decision framework with clear roles."},
                {"stage": "S", "text": "I set organizational norms for human-AI decision boundaries."},
            ]
        },
    ],
    4: [
        {
            "id": "epias_l4_harness",
            "dimension": "harness_maturity",
            "question": "How mature are your autonomous AI harnesses?",
            "options": [
                {"stage": "E", "text": "Experimenting with agent pipelines \u2014 results need heavy validation."},
                {"stage": "P", "text": "Operating harnesses with repeatable execution, evals, and retries."},
                {"stage": "I", "text": "End-to-end workflows run autonomously with comprehensive eval suites."},
                {"stage": "A", "text": "I've built production-grade agent infrastructure others operate."},
                {"stage": "S", "text": "I define governance for autonomous systems at scale."},
            ]
        },
        {
            "id": "epias_l4_evals",
            "dimension": "evaluation",
            "question": "How do your evaluation systems work?",
            "options": [
                {"stage": "E", "text": "Manual review of agent outputs after each run."},
                {"stage": "P", "text": "Automated pass/fail gates with manual escalation for edge cases."},
                {"stage": "I", "text": "Comprehensive eval suites with structure, quality, and regression gates."},
                {"stage": "A", "text": "Self-improving eval pipelines with eval-driven development."},
                {"stage": "S", "text": "I maintain org-level eval infrastructure and define risk thresholds."},
            ]
        },
        {
            "id": "epias_l4_autonomy",
            "dimension": "system_autonomy",
            "question": "How autonomous are your AI systems?",
            "options": [
                {"stage": "E", "text": "Semi-autonomous \u2014 I still check in frequently and debug manually."},
                {"stage": "P", "text": "Run reliably with escalation paths \u2014 I handle exceptions."},
                {"stage": "I", "text": "Exception classes and recovery paths are documented; the system self-heals."},
                {"stage": "A", "text": "Others operate my systems and interpret failures independently."},
                {"stage": "S", "text": "I define accountability and approval frameworks for autonomous AI."},
            ]
        },
        {
            "id": "epias_l4_infrastructure",
            "dimension": "shared_infra",
            "question": "How do others interact with your AI infrastructure?",
            "options": [
                {"stage": "E", "text": "It's personal tooling \u2014 only I use it."},
                {"stage": "P", "text": "Teammates can trigger runs with my guidance."},
                {"stage": "I", "text": "Others trigger runs and interpret results independently."},
                {"stage": "A", "text": "My harness is maintained like a product with docs and onboarding."},
                {"stage": "S", "text": "I run organizational AI infrastructure serving multiple teams."},
            ]
        },
        {
            "id": "epias_l4_governance",
            "dimension": "governance",
            "question": "What governance do you have for automated AI work?",
            "options": [
                {"stage": "E", "text": "Minimal \u2014 I trust my own judgment to catch problems."},
                {"stage": "P", "text": "Logging and diffs for auditability; rollback plans exist."},
                {"stage": "I", "text": "Formal decision traces, approval gates, and rollback procedures."},
                {"stage": "A", "text": "Governance frameworks that other teams adopt."},
                {"stage": "S", "text": "Enterprise-level AI risk management and trust standards."},
            ]
        },
    ],
    5: [
        {
            "id": "epias_l5_goals",
            "dimension": "goal_setting",
            "question": "How do you set goals for fully autonomous AI systems?",
            "options": [
                {"stage": "E", "text": "Exploring goal-setting interfaces \u2014 exception handling is unclear."},
                {"stage": "P", "text": "I set approval gates and quality bars consistently."},
                {"stage": "I", "text": "Autonomous workflows with clear, documented escalation paths."},
                {"stage": "A", "text": "I've designed goal-setting and approval systems others trust."},
                {"stage": "S", "text": "I define enterprise governance for fully autonomous AI."},
            ]
        },
        {
            "id": "epias_l5_oversight",
            "dimension": "oversight",
            "question": "How do you maintain oversight of autonomous systems?",
            "options": [
                {"stage": "E", "text": "Manual spot-checking of outputs."},
                {"stage": "P", "text": "Routine review of autonomous outputs on a schedule."},
                {"stage": "I", "text": "Exception-handling systems with clear escalation paths."},
                {"stage": "A", "text": "Reusable governance frameworks for autonomous oversight."},
                {"stage": "S", "text": "Organizational AI risk and trust standards."},
            ]
        },
        {
            "id": "epias_l5_trust",
            "dimension": "trust_calibration",
            "question": "How well-calibrated is your trust in autonomous AI?",
            "options": [
                {"stage": "E", "text": "I'm not sure when to trust and when to verify."},
                {"stage": "P", "text": "I know the boundaries of what I can trust."},
                {"stage": "I", "text": "Trust boundaries are documented with validation evidence."},
                {"stage": "A", "text": "I've designed trust frameworks others use to calibrate."},
                {"stage": "S", "text": "I set organizational trust policies and approval frameworks."},
            ]
        },
        {
            "id": "epias_l5_adaptation",
            "dimension": "system_adaptation",
            "question": "How do your autonomous systems adapt and improve?",
            "options": [
                {"stage": "E", "text": "They don't \u2014 I manually update them when things break."},
                {"stage": "P", "text": "I review and update configurations periodically."},
                {"stage": "I", "text": "Systems have feedback loops that surface improvement opportunities."},
                {"stage": "A", "text": "Self-improving systems with documented evolution patterns."},
                {"stage": "S", "text": "I govern system evolution across the organization."},
            ]
        },
        {
            "id": "epias_l5_accountability",
            "dimension": "organizational_accountability",
            "question": "Who is accountable for autonomous AI decisions?",
            "options": [
                {"stage": "E", "text": "Unclear \u2014 accountability isn't well defined."},
                {"stage": "P", "text": "I'm personally accountable for everything the system does."},
                {"stage": "I", "text": "Clear RACI with documented decision authority."},
                {"stage": "A", "text": "Accountability frameworks adopted by multiple teams."},
                {"stage": "S", "text": "Enterprise accountability and compliance standards."},
            ]
        },
    ],
}


def get_all_sae_questions() -> list:
    """Return all SAE level identification questions."""
    return SAE_QUESTIONS


def get_epias_questions(sae_level: int) -> list:
    """Return EPIAS maturity questions for a specific SAE level."""
    return EPIAS_QUESTIONS.get(sae_level, EPIAS_QUESTIONS.get(1, []))

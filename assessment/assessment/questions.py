"""Self-assessment questionnaire definitions for E-P-I-A-S x SAE Framework.

Two tracks: Design and UX Research. Same question IDs and option
level/stage values — only the human-readable text differs.
Scoring (scorer.py) is role-independent.

SAE levels map to responsibility shift (adapted from SAE J3016):
  L0: You own everything (no AI)
  L1: You own every AI moment (AI assists)
  L2: You own every integration (AI builds bounded chunks)
  L3: You own the checkpoints (AI drives within conditions)
  L4: You own the rules (AI executes autonomously)
  L5: You own the goals (AI drives everything)

EPIAS stages map to depth of internalization:
  E: Explorer — trying, inconsistent, learning
  P: Practitioner — reliable, personal, in my head
  I: Integrator — documented, traceable, reviewable
  A: Architect — others use my systems independently
  S: Steward — organizational standards, mentorship
"""

# ---------------------------------------------------------------------------
# SAE Questions — Design Track
# ---------------------------------------------------------------------------

SAE_QUESTIONS_DESIGN = [
    {
        "id": "sae_tools",
        "question": "Which best describes how you regularly use AI in your work?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI tools in my work."},
            {"level": 1, "text": "I use AI for one task at a time \u2014 chat, generate, review, repeat."},
            {"level": 2, "text": "I give AI a spec and it produces usable pieces \u2014 I assemble and integrate them."},
            {"level": 3, "text": "I run multi-step AI workflows with checkpoints \u2014 work persists across sessions."},
            {"level": 4, "text": "I run autonomous AI systems that execute, evaluate, and self-correct without me present."},
            {"level": 5, "text": "AI handles my workflow end-to-end \u2014 I set goals and review exceptions."},
        ]
    },
    {
        "id": "sae_qa",
        "question": "Which best describes how you check AI output quality?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI, so there\u2019s nothing to check."},
            {"level": 1, "text": "I read and judge every AI output myself \u2014 no formal process."},
            {"level": 2, "text": "I use a defined checklist before accepting each piece."},
            {"level": 3, "text": "Automated checks are built into my workflow \u2014 I review what passes."},
            {"level": 4, "text": "Eval suites decide pass, retry, or escalate \u2014 I only see flagged exceptions."},
            {"level": 5, "text": "Self-correcting QA loops run end-to-end \u2014 I review trends, not individual outputs."},
        ]
    },
    {
        "id": "sae_laptop",
        "question": "Which best describes what happens to your AI work when you step away?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI, so nothing changes when I step away."},
            {"level": 1, "text": "Everything stops \u2014 each session is standalone, so I start fresh every time."},
            {"level": 2, "text": "AI resets \u2014 but I\u2019ve built reusable specs and prompts, so I reproduce results quickly."},
            {"level": 3, "text": "AI pauses \u2014 but my workspace keeps files, history, and context, so I pick up mid-workflow."},
            {"level": 4, "text": "Work continues without me \u2014 agents run, evaluate, and retry on their own."},
            {"level": 5, "text": "Work runs indefinitely \u2014 I review exception reports, not task progress."},
        ]
    },
    {
        "id": "sae_prompting",
        "question": "Which best describes how you instruct AI?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI."},
            {"level": 1, "text": "I type prompts one at a time and iterate until the output looks right."},
            {"level": 2, "text": "I write structured prompts with context, constraints, and output format \u2014 one task at a time."},
            {"level": 3, "text": "I maintain context systems (rules files, example libraries) that guide multi-step workflows."},
            {"level": 4, "text": "I configure autonomous pipelines with eval gates and self-correction \u2014 the system adjusts its own approach."},
            {"level": 5, "text": "I set goals and constraints \u2014 the system writes and revises its own instructions."},
        ]
    },
    {
        "id": "sae_outputs",
        "question": "Which best describes the deliverables AI routinely produces for you?",
        "options": [
            {"level": 0, "text": "None \u2014 I produce everything myself."},
            {"level": 1, "text": "Ideas and rough drafts \u2014 I do substantial rework before anything ships."},
            {"level": 2, "text": "Usable individual deliverables from a clear spec \u2014 I assemble the final product."},
            {"level": 3, "text": "Coordinated multi-part outputs \u2014 AI handles connected steps, I QA the result."},
            {"level": 4, "text": "End-to-end deliverables that are generated, tested, and revised by pipeline \u2014 I review what ships."},
            {"level": 5, "text": "Complete products with autonomous iteration \u2014 AI handles the full create-test-refine loop."},
        ]
    },
    {
        "id": "sae_reuse",
        "question": "Which best describes who can use your AI setup?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI workflows."},
            {"level": 1, "text": "Just me, informally \u2014 I have saved prompts I copy-paste, but nothing structured."},
            {"level": 2, "text": "Just me, systematically \u2014 I maintain reusable templates and specs for my own use."},
            {"level": 3, "text": "My team \u2014 I maintain shared workflows and context libraries others can run."},
            {"level": 4, "text": "My organization \u2014 I maintain production infrastructure others operate as a service."},
            {"level": 5, "text": "Anyone \u2014 self-improving pipelines that adapt to new users and contexts."},
        ]
    },
]

# ---------------------------------------------------------------------------
# SAE Questions — UX Research Track
# ---------------------------------------------------------------------------

SAE_QUESTIONS_UXR = [
    {
        "id": "sae_tools",
        "question": "Which best describes how you regularly use AI in your research?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI tools in my research."},
            {"level": 1, "text": "I use AI for one task at a time \u2014 summarize, code, draft, repeat."},
            {"level": 2, "text": "I give AI a research brief and it produces synthesis outputs \u2014 I validate and integrate them."},
            {"level": 3, "text": "I run multi-step research pipelines with verification checkpoints \u2014 work persists across sessions."},
            {"level": 4, "text": "I run autonomous research systems that execute, verify, and self-correct without me present."},
            {"level": 5, "text": "AI handles my research workflow end-to-end \u2014 I set goals and review exceptions."},
        ]
    },
    {
        "id": "sae_qa",
        "question": "Which best describes how you verify AI research output?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI, so there\u2019s nothing to verify."},
            {"level": 1, "text": "I check every AI output against source material myself \u2014 no formal process."},
            {"level": 2, "text": "I use a defined verification checklist before accepting each synthesis."},
            {"level": 3, "text": "Automated verification gates are built into my pipeline \u2014 I review what passes."},
            {"level": 4, "text": "Validation suites decide pass, retry, or escalate \u2014 I only see flagged exceptions."},
            {"level": 5, "text": "Self-correcting verification loops run end-to-end \u2014 I review trends, not individual outputs."},
        ]
    },
    {
        "id": "sae_laptop",
        "question": "Which best describes what happens to your AI research when you step away?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI, so nothing changes when I step away."},
            {"level": 1, "text": "Everything stops \u2014 each session is standalone, so I start fresh every time."},
            {"level": 2, "text": "AI resets \u2014 but I\u2019ve built reusable briefs and prompts, so I reproduce results quickly."},
            {"level": 3, "text": "AI pauses \u2014 but my workspace keeps files, history, and context, so I pick up mid-pipeline."},
            {"level": 4, "text": "Research continues without me \u2014 pipelines run, verify, and retry on their own."},
            {"level": 5, "text": "Research runs indefinitely \u2014 I review exception reports, not task progress."},
        ]
    },
    {
        "id": "sae_prompting",
        "question": "Which best describes how you instruct AI in your research?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI."},
            {"level": 1, "text": "I type prompts one at a time and verify each output against source."},
            {"level": 2, "text": "I write structured research inputs with codebooks, constraints, and traceability requirements \u2014 one task at a time."},
            {"level": 3, "text": "I maintain research context systems (verification rules, codebooks, escalation triggers) that guide multi-step pipelines."},
            {"level": 4, "text": "I configure autonomous pipelines with validation gates and confidence thresholds \u2014 the system adjusts its own approach."},
            {"level": 5, "text": "I set research goals and constraints \u2014 the system writes and revises its own instructions."},
        ]
    },
    {
        "id": "sae_outputs",
        "question": "Which best describes the research outputs AI routinely produces for you?",
        "options": [
            {"level": 0, "text": "None \u2014 I produce everything myself."},
            {"level": 1, "text": "Summaries and draft screeners \u2014 I do substantial verification before anything is used."},
            {"level": 2, "text": "Usable themes and coded segments from clear inputs \u2014 I assemble the final analysis."},
            {"level": 3, "text": "Coordinated multi-study synthesis \u2014 AI handles connected steps, I validate the result."},
            {"level": 4, "text": "End-to-end insight digests that are generated, validated, and revised by pipeline \u2014 I review what ships."},
            {"level": 5, "text": "Complete research outputs with autonomous iteration \u2014 AI handles the full analyze-verify-refine loop."},
        ]
    },
    {
        "id": "sae_reuse",
        "question": "Which best describes who can use your AI research setup?",
        "options": [
            {"level": 0, "text": "I don\u2019t use AI workflows."},
            {"level": 1, "text": "Just me, informally \u2014 I have saved prompts and checklists I copy-paste, but nothing structured."},
            {"level": 2, "text": "Just me, systematically \u2014 I maintain reusable templates and codebooks for my own use."},
            {"level": 3, "text": "My team \u2014 I maintain shared research workflows and codebooks others can run."},
            {"level": 4, "text": "My organization \u2014 I maintain production research infrastructure others operate as a service."},
            {"level": 5, "text": "Anyone \u2014 self-improving pipelines that adapt to new researchers and contexts."},
        ]
    },
]


# ---------------------------------------------------------------------------
# EPIAS Questions — Design Track (5 per SAE level)
# ---------------------------------------------------------------------------

EPIAS_QUESTIONS_DESIGN = {
    0: [
        {
            "id": "epias_l0_intake_to_screens",
            "dimension": "From request to screens",
            "question": "Which best describes how you turn vague requests into initial wireframes or screens?",
            "options": [
                {"stage": "E", "text": "I start fresh each time and I’m still figuring out what steps work — the path and the outputs vary a lot."},
                {"stage": "P", "text": "I have a sequence that usually works, but it’s mostly in my head — it isn’t something others can reliably follow."},
                {"stage": "I", "text": "I follow a documented flow with templates and checkpoints — others can review the artifacts and understand how I got to the design."},
                {"stage": "A", "text": "My flow is packaged as a shared playbook and starter files — other designers run it end-to-end without needing me."},
                {"stage": "S", "text": "I set and evolve the org’s design process standards — I coach teams and make sure projects actually use them."},
            ]
        },
        {
            "id": "epias_l0_rationale_traceability",
            "dimension": "Decision rationale and traceability",
            "question": "Which best describes your practice for capturing and tracing design decision rationale?",
            "options": [
                {"stage": "E", "text": "I make decisions as I go and rarely capture why — later I have to reconstruct my thinking from memory."},
                {"stage": "P", "text": "I can explain my decisions, but it’s mostly in my head or scattered in chats — others can’t easily trace it later."},
                {"stage": "I", "text": "I record key decisions in the file and a decision log — teammates can trace rationale to specific screens and constraints."},
                {"stage": "A", "text": "Teams use my decision-log format and checkpoints — they can defend choices without pulling me into every question."},
                {"stage": "S", "text": "I define how rationale is captured for the org — I mentor leads and ensure high-stakes decisions stay traceable."},
            ]
        },
        {
            "id": "epias_l0_pattern_reuse",
            "dimension": "Component and pattern reuse",
            "question": "Which best describes your component and UI pattern reuse practice after projects ship?",
            "options": [
                {"stage": "E", "text": "I often rebuild similar UI each project because I’m still figuring out patterns — reuse is inconsistent."},
                {"stage": "P", "text": "I reuse my own components and snippets, but they’re personal — other designers don’t reliably adopt them."},
                {"stage": "I", "text": "I maintain documented components with usage notes and examples — others can reuse them and know when not to."},
                {"stage": "A", "text": "My components and patterns are the default starting point for multiple teams — they use them without my help."},
                {"stage": "S", "text": "I steward the design system for the org — I govern contributions, deprecations, and consistency across products."},
            ]
        },
        {
            "id": "epias_l0_design_reviews",
            "dimension": "Design review practice",
            "question": "Which best describes your design review and critique practice for work you produce?",
            "options": [
                {"stage": "E", "text": "Feedback is ad hoc and I’m still learning what “good” looks like — reviews depend on who happens to look."},
                {"stage": "P", "text": "I get reliable feedback from a few trusted people, but it’s informal — the approach doesn’t scale beyond me."},
                {"stage": "I", "text": "I run documented design reviews with criteria and notes — decisions and follow-ups are visible to the team."},
                {"stage": "A", "text": "Other designers use my review checklist and cadence — quality improves even when I’m not in the room."},
                {"stage": "S", "text": "I set org-wide review standards and train reviewers — I monitor recurring issues and raise the bar across teams."},
            ]
        },
        {
            "id": "epias_l0_handoff_to_engineering",
            "dimension": "Handoff and build readiness",
            "question": "Which best describes your handoff and build-readiness practice with engineers?",
            "options": [
                {"stage": "E", "text": "I hand off screens and answer questions as they come — I’m still figuring out what engineers need upfront."},
                {"stage": "P", "text": "I create specs that usually work, but they’re tailored each time — the handoff process lives with me."},
                {"stage": "I", "text": "I provide consistent specs for states and behavior and track changes — engineers can review and comment in one place."},
                {"stage": "A", "text": "My handoff templates and conventions are used by other designers — engineering can implement with minimal back-and-forth."},
                {"stage": "S", "text": "I set org standards for design-to-dev handoff — I align Design and Engineering on expectations and coach adoption."},
            ]
        },
    ],
    1: [
        {
            "id": "epias_l1_prompt_organization",
            "dimension": "Prompt organization",
            "question": "When you use chat AI for design tasks like UI copy, wireframes, or component specs, how do you keep track of the prompts that worked?",
            "options": [
                {"stage": "E", "text": "I mostly improvise prompts and results vary—I'm still figuring out what reliably works."},
                {"stage": "P", "text": "I reuse a few go-to prompts from my own notes—it's personal and only I really use it."},
                {"stage": "I", "text": "I keep a documented set of prompts with examples and context—others can review what I asked and why."},
                {"stage": "A", "text": "I package prompts and examples so other designers can use them and get solid outputs—without me walking them through."},
                {"stage": "S", "text": "I set the organization’s standards for how prompts are written and stored for design work—and I coach teams on them."},
            ]
        },
        {
            "id": "epias_l1_ai_judgment",
            "dimension": "AI judgment",
            "question": "How do you decide whether an AI-suggested layout, flow, or component spec is ready to bring into a design review?",
            "options": [
                {"stage": "E", "text": "I go with my gut and sometimes miss issues—I'm still learning what to check for."},
                {"stage": "P", "text": "I use my own mental checklist for UX and accessibility—it's in my head and others don’t see the criteria."},
                {"stage": "I", "text": "I use a written checklist tied to our design principles and system rules—someone else can audit how I judged it."},
                {"stage": "A", "text": "I created a review rubric the team uses to vet AI outputs before critiques—quality holds without me."},
                {"stage": "S", "text": "I define org-wide quality gates for AI-assisted design and mentor reviewers—so judgment is consistent across teams."},
            ]
        },
        {
            "id": "epias_l1_output_consistency",
            "dimension": "Output consistency",
            "question": "Which best describes the consistency of your AI-assisted design outputs across a feature?",
            "options": [
                {"stage": "E", "text": "They often don’t match each other and I rewrite a lot—I'm still figuring out how to steer consistency."},
                {"stage": "P", "text": "I can usually keep things consistent for my own screens—others can’t easily reproduce how I got there."},
                {"stage": "I", "text": "I maintain documented constraints like tone, tokens, and component rules that I reuse—outputs are repeatable and reviewable."},
                {"stage": "A", "text": "I provide shared constraint snippets and examples the team reuses—others get consistent results without my involvement."},
                {"stage": "S", "text": "I own and govern the org’s consistency standards for AI-assisted design—teams follow them across products."},
            ]
        },
        {
            "id": "epias_l1_traceability",
            "dimension": "Traceability",
            "question": "Which best describes your traceability practice for AI-influenced design decisions?",
            "options": [
                {"stage": "E", "text": "I usually paste the final result into Figma or a doc and move on—prompts and reasoning get lost."},
                {"stage": "P", "text": "I keep the chat history for myself and sometimes link it—it's not consistent and mostly only helps me."},
                {"stage": "I", "text": "I consistently attach prompts, outputs, and my edits to the related screen or spec—others can trace decisions during review."},
                {"stage": "A", "text": "I set up simple templates and a team workflow for capturing AI provenance—people do it without me reminding them."},
                {"stage": "S", "text": "I define the organization’s traceability expectations for AI-assisted design and monitor adoption—so audits and handoffs are reliable."},
            ]
        },
        {
            "id": "epias_l1_learning_loop",
            "dimension": "Learning loop",
            "question": "Which best describes your learning loop after critiques on AI-assisted design work?",
            "options": [
                {"stage": "E", "text": "I tweak the next prompt on the fly—lessons don’t stick and results stay inconsistent."},
                {"stage": "P", "text": "I keep a few personal do’s and don’ts from feedback—it's in my head and not shared."},
                {"stage": "I", "text": "I document what worked, what failed, and the updated prompt next to the deliverable—others can learn from it."},
                {"stage": "A", "text": "I maintain a shared playbook teams use to improve AI-assisted design iterations—without my direct help."},
                {"stage": "S", "text": "I run org-wide learning loops on AI-assisted design patterns and pitfalls—and I mentor teams based on them."},
            ]
        },
    ],
    2: [
        {
            "id": "epias_l2_spec_clarity",
            "dimension": "Spec clarity for AI",
            "question": "When you ask AI to generate a screen, flow, or component, how do you usually write the spec it works from?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out what details matter—sometimes AI nails it, other times I realize I forgot key constraints."},
                {"stage": "P", "text": "I have a reliable way to brief AI, but it’s mostly in my head and I’m the only one who can write it well."},
                {"stage": "I", "text": "I use a documented brief format with examples—others can review it, but I still need to tailor it for each case."},
                {"stage": "A", "text": "I’ve built spec templates and examples that others use to get solid outputs without my help—within our team’s design work."},
                {"stage": "S", "text": "I set the organization’s standard for AI-ready design briefs and coach teams on it—adoption and compliance are part of my remit."},
            ]
        },
        {
            "id": "epias_l2_chunking",
            "dimension": "Chunking into bounded asks",
            "question": "How do you break a design problem into AI-sized asks so the outputs come back usable and consistent?",
            "options": [
                {"stage": "E", "text": "I’m still experimenting with how to split the work—sometimes I ask for too much at once and the output gets messy."},
                {"stage": "P", "text": "I know how to chunk requests in a way that works for me, but I do it by feel and haven’t made it shareable."},
                {"stage": "I", "text": "I follow a documented breakdown pattern (flows, states, components)—others can trace what I asked for and why."},
                {"stage": "A", "text": "I’ve created a repeatable breakdown approach others run without me—so they get coherent sets of screens and states."},
                {"stage": "S", "text": "I define how teams should chunk design work for AI across the org—then I mentor and tune the approach as needs change."},
            ]
        },
        {
            "id": "epias_l2_integration",
            "dimension": "Integration into the product/design system",
            "question": "Which best describes how you integrate AI-generated designs into your design system?",
            "options": [
                {"stage": "E", "text": "I mostly drop the output into the file and adjust until it looks right—consistency with the system is hit-or-miss."},
                {"stage": "P", "text": "I integrate AI output in a consistent way, but it relies on my personal judgment and others don’t follow the same approach."},
                {"stage": "I", "text": "I integrate using documented rules (tokens, components, naming, variants)—others can review the changes and rationale."},
                {"stage": "A", "text": "I’ve set up integration patterns and starter files others can use without me—so AI drafts land in our system cleanly."},
                {"stage": "S", "text": "I govern how AI-generated design is integrated org-wide—standards, review expectations, and system alignment are enforced."},
            ]
        },
        {
            "id": "epias_l2_qa_rigor",
            "dimension": "QA and design review rigor",
            "question": "Which best describes your QA and design review rigor for AI-generated design deliverables?",
            "options": [
                {"stage": "E", "text": "I’m still learning what to QA—sometimes I miss basics like states, empty cases, or accessibility until late."},
                {"stage": "P", "text": "I have a personal QA routine that catches most issues, but it isn’t written down and no one else runs it."},
                {"stage": "I", "text": "I use a documented checklist for QA and review notes—others can audit what was checked and what was deferred."},
                {"stage": "A", "text": "I’ve built QA checklists and review templates others use without me—so outputs are consistently review-ready."},
                {"stage": "S", "text": "I set QA standards for AI-assisted design across the org—training, calibration, and governance are part of my role."},
            ]
        },
        {
            "id": "epias_l2_reusability",
            "dimension": "Reusable prompts, examples, and assets",
            "question": "How reusable is what you’ve built to get good L2 AI outputs in design (prompts, example specs, starter files, component recipes)?",
            "options": [
                {"stage": "E", "text": "I have scattered prompts and examples I try here and there—nothing consistently works across projects yet."},
                {"stage": "P", "text": "I maintain a personal set of prompts and files that work for me, but they’re not organized for anyone else to use."},
                {"stage": "I", "text": "My prompts, examples, and assets are documented and versioned—others can review them, but they still need my guidance to apply them."},
                {"stage": "A", "text": "Others use my shared library of prompts and design starters without my help—results are reliable for our team’s common use cases."},
                {"stage": "S", "text": "I curate and govern the org-wide library of AI design patterns—standards, ownership, and ongoing maintenance are formalized."},
            ]
        },
    ],
    3: [
        {
            "id": "epias_l3_workflow_repeatability",
            "dimension": "Workflow repeatability",
            "question": "Which best describes your AI-assisted design workflow repeatability across projects?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out the steps—each run is different and results are inconsistent."},
                {"stage": "P", "text": "I have a reliable routine, but it lives in my head and only I can run it smoothly."},
                {"stage": "I", "text": "The workflow is documented with clear checkpoints—others can review it and follow it."},
                {"stage": "A", "text": "Others use my shared workflow without my help—deliverables stay consistent across projects."},
                {"stage": "S", "text": "I set the organization’s standard guided-automation workflow and mentor teams—adoption and reliability are governed."},
            ]
        },
        {
            "id": "epias_l3_context_packaging",
            "dimension": "Context engineering for consistency",
            "question": "Which best describes your context-engineering practice for keeping AI outputs on-brand and consistent?",
            "options": [
                {"stage": "E", "text": "I paste whatever context I have—I’m still learning what’s needed, and the AI often drifts."},
                {"stage": "P", "text": "I have a personal context pack (brand, components, examples), but it’s not shared and others don’t use it."},
                {"stage": "I", "text": "I maintain a documented, versioned context library—others can review it and know what changed."},
                {"stage": "A", "text": "Teams can grab my context packs and run workflows without me—new work stays consistent from the first pass."},
                {"stage": "S", "text": "I set org-wide standards for context packs and how they’re updated—I mentor teams and govern consistency."},
            ]
        },
        {
            "id": "epias_l3_failure_handling",
            "dimension": "Failure handling and recovery",
            "question": "Which best describes your AI-related failure handling and recovery practice in product design workflows?",
            "options": [
                {"stage": "E", "text": "I mostly retry and tweak prompts—I’m still figuring out why failures happen and results vary."},
                {"stage": "P", "text": "I have my own way to catch and fix issues, but it’s not written down and only I apply it."},
                {"stage": "I", "text": "I use a documented checkpoint QA and rollback process—issues are logged and traceable."},
                {"stage": "A", "text": "Others use my playbooks to recover without me—work rarely stalls when the AI goes off-track."},
                {"stage": "S", "text": "I govern org policy for AI-assisted design QA and risk—I review patterns and mentor teams on prevention."},
            ]
        },
        {
            "id": "epias_l3_tooling_operationalization",
            "dimension": "Tooling and workflow persistence",
            "question": "Which best describes your AI design tooling and workflow persistence setup across sessions?",
            "options": [
                {"stage": "E", "text": "My setup is ad hoc—prompts, files, and checkpoints get lost, and I rework things often."},
                {"stage": "P", "text": "I’ve pieced together a setup that works for me, but it lives on my machine and in my notes."},
                {"stage": "I", "text": "The setup is documented and reproducible—others can install it and run the same workflow."},
                {"stage": "A", "text": "I maintain a shared toolkit or template workspace others use without me—updates don’t break their flow."},
                {"stage": "S", "text": "I choose and govern the organization’s tooling approach—access, security, and support are standardized."},
            ]
        },
        {
            "id": "epias_l3_decision_traceability",
            "dimension": "Decision ownership and traceability",
            "question": "Which best describes your practice for documenting AI versus human design decisions in reviews?",
            "options": [
                {"stage": "E", "text": "I can’t always separate AI output from my decisions—my notes are incomplete and inconsistent."},
                {"stage": "P", "text": "I track decisions in my own way, but it’s personal and not easy for others to audit."},
                {"stage": "I", "text": "I keep reviewable artifacts that separate AI output from design decisions—rationale links to specs and feedback."},
                {"stage": "A", "text": "Teams use my templates to defend decisions without me—stakeholders can follow the thread end-to-end."},
                {"stage": "S", "text": "I set org standards for attribution and decision records—I mentor reviewers and govern compliance."},
            ]
        },
    ],
    4: [
        {
            "id": "epias_l4_quality_evals",
            "dimension": "Automated quality evaluation",
            "question": "Which best describes your automated quality evaluation for AI-generated designs?",
            "options": [
                {"stage": "E", "text": "I mostly eyeball it after the fact — I’m still figuring out reliable checks and the results are inconsistent."},
                {"stage": "P", "text": "I use a personal checklist I’ve built up in my head — it works for me, but others don’t really use it."},
                {"stage": "I", "text": "I run documented automated checks with saved results — others can review what passed, what failed, and why."},
                {"stage": "A", "text": "My team runs the same automated checks in a shared harness — they get clear pass/fail output without needing me."},
                {"stage": "S", "text": "I set org-wide quality bars and required checks — I mentor teams on them and govern exceptions."},
            ]
        },
        {
            "id": "epias_l4_unattended_recovery",
            "dimension": "Unattended runs and recovery",
            "question": "Which best describes your practice for handling failures in unattended AI design runs?",
            "options": [
                {"stage": "E", "text": "I usually find out later and manually clean it up — I don’t yet have a reliable way to prevent or recover from failures."},
                {"stage": "P", "text": "I have a few guardrails and habits I rely on — but they’re personal and I’m the one who has to step in."},
                {"stage": "I", "text": "I use documented checkpoints and rollback steps — failures are logged so others can follow what happened."},
                {"stage": "A", "text": "Others can rerun, roll back, or pause the system using my controls — they don’t need me to recover safely."},
                {"stage": "S", "text": "I run a consistent incident process across teams — we review failures, update standards, and govern risk."},
            ]
        },
        {
            "id": "epias_l4_design_system_alignment",
            "dimension": "Design system alignment at scale",
            "question": "Which best describes your practice for keeping autonomous UI generation aligned with your design system?",
            "options": [
                {"stage": "E", "text": "It drifts from the design system a lot — I’m still figuring out how to keep it consistent."},
                {"stage": "P", "text": "I have my own notes and preferences for keeping it aligned — but it mostly lives with me and isn’t adopted by others."},
                {"stage": "I", "text": "I’ve documented the rules and mappings to our tokens and components — changes are traceable and reviewable."},
                {"stage": "A", "text": "Other designers use my setup to generate on-system components and screens — it works without my involvement."},
                {"stage": "S", "text": "I set and govern the org’s system-alignment rules — I mentor teams and manage how patterns evolve."},
            ]
        },
        {
            "id": "epias_l4_decision_traceability",
            "dimension": "Decision logging and reviewability",
            "question": "Which best describes your AI design decision logging and reviewability practice?",
            "options": [
                {"stage": "E", "text": "Decisions are mostly implicit in the output — I’m still figuring out how to make the reasoning consistent and reviewable."},
                {"stage": "P", "text": "I can usually explain what happened from memory — but it’s personal and not reliably captured for others."},
                {"stage": "I", "text": "Decisions are documented with links to inputs and outcomes — others can review the trail and comment."},
                {"stage": "A", "text": "My workflow produces decision logs that others use in reviews — they can audit choices without needing me present."},
                {"stage": "S", "text": "I set expectations for decision traceability across the org — I coach teams and govern review gates."},
            ]
        },
        {
            "id": "epias_l4_shared_harness_infra",
            "dimension": "Shared harness infrastructure",
            "question": "Which best describes your shared AI design harness infrastructure for autonomous workflows?",
            "options": [
                {"stage": "E", "text": "They’d have to copy what I’m doing and hope it works — I’m still figuring out a repeatable setup."},
                {"stage": "P", "text": "I could get them going with my own templates and explanations — but it’s basically my personal setup."},
                {"stage": "I", "text": "I have documented onboarding, templates, and safeguards — others can run it and you can see what happened."},
                {"stage": "A", "text": "It’s a shared service with clear entry points and defaults — designers use it successfully without my help."},
                {"stage": "S", "text": "I govern how the org uses shared AI design infrastructure — I set standards, train people, and manage access and risk."},
            ]
        },
    ],
    5: [
        {
            "id": "epias_l5_goal_definition",
            "dimension": "Goal framing & acceptance criteria",
            "question": "Which best describes your goal framing and acceptance-criteria practice for AI-driven design tasks?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out how to write goals the AI can follow — I often rerun because “done” wasn’t clear."},
                {"stage": "P", "text": "I can usually write a solid goal and constraints, but it’s a personal recipe in my head — nobody else uses it."},
                {"stage": "I", "text": "I use a documented brief template with explicit success checks and constraints — others can review what I asked for."},
                {"stage": "A", "text": "I’ve built reusable goal templates and guardrails that teammates can use to get consistent outputs without my help."},
                {"stage": "S", "text": "I set the organization’s standard for AI design briefs and acceptance criteria — I coach teams and update it based on outcomes."},
            ]
        },
        {
            "id": "epias_l5_exception_triage",
            "dimension": "Exception handling & escalation",
            "question": "Which best describes your exception handling and escalation practice in AI-driven design workflows?",
            "options": [
                {"stage": "E", "text": "I jump in case-by-case when something looks off — I’m still learning which exceptions matter."},
                {"stage": "P", "text": "I have my own way to triage AI flags, but it lives in my head — others rely on me to interpret what to do."},
                {"stage": "I", "text": "Exceptions are categorized and logged with a written playbook — anyone can follow the steps and see what happened."},
                {"stage": "A", "text": "I’ve built an exception workflow that routes issues to the right reviewer and resolves most cases without my involvement."},
                {"stage": "S", "text": "I set org-wide thresholds and escalation rules for AI exceptions — I monitor patterns and tighten governance when risk rises."},
            ]
        },
        {
            "id": "epias_l5_quality_gates",
            "dimension": "Trust calibration & release readiness",
            "question": "Which best describes your trust calibration and release readiness for AI-generated design deliverables?",
            "options": [
                {"stage": "E", "text": "My checks are inconsistent — sometimes I hand off AI work I later end up redoing."},
                {"stage": "P", "text": "I have a dependable personal review pass before handoff, but it isn’t written down — others can’t replicate my bar."},
                {"stage": "I", "text": "I use a documented review checklist tied to requirements and the design system — others can audit my sign-off."},
                {"stage": "A", "text": "I’ve built shared quality gates that catch common issues automatically — teammates can ship using the same gates without me."},
                {"stage": "S", "text": "I define the organization’s quality and risk standards for AI-produced design deliverables — I train reviewers and run periodic audits."},
            ]
        },
        {
            "id": "epias_l5_alignment_updates",
            "dimension": "System alignment & ongoing adaptation",
            "question": "Which best describes how you keep AI design workflows aligned with evolving systems and stakeholders?",
            "options": [
                {"stage": "E", "text": "I tweak prompts or examples when outputs drift — I haven’t found a reliable way to keep it aligned over time."},
                {"stage": "P", "text": "I maintain personal examples and notes to keep the AI on-brand, but they’re in my own workspace — nobody else benefits."},
                {"stage": "I", "text": "Changes to patterns, components, and rules are documented and versioned — others can see what changed and why."},
                {"stage": "A", "text": "I’ve built a shared source-of-truth library the workflow pulls from automatically — teams stay aligned without my help."},
                {"stage": "S", "text": "I govern how AI consumes design-system sources of truth and stakeholder inputs — I coordinate updates across teams and approve breaking changes."},
            ]
        },
        {
            "id": "epias_l5_accountability_traceability",
            "dimension": "Accountability & decision traceability",
            "question": "Which best describes your practice for documenting accountability and rationale for AI-driven design decisions?",
            "options": [
                {"stage": "E", "text": "I usually can’t point to a clear trail for “why” — I’m still figuring out how to capture rationale from AI-led work."},
                {"stage": "P", "text": "I can explain decisions from memory, but the rationale isn’t recorded — stakeholders have to trust my recap."},
                {"stage": "I", "text": "Key decisions are traceable to the brief, constraints, and review notes — others can follow the reasoning after the fact."},
                {"stage": "A", "text": "I’ve set up a system that automatically produces a decision log linked to artifacts — teams can answer “why” without me."},
                {"stage": "S", "text": "I set org standards for ownership and decision records in AI-led design — I arbitrate disputes and enforce accountability."},
            ]
        },
    ],
}


# ---------------------------------------------------------------------------
# EPIAS Questions — UX Research Track (5 per SAE level)
# ---------------------------------------------------------------------------

EPIAS_QUESTIONS_UXR = {
    0: [
        {
            "id": "epias_l0_synthesis_coding",
            "dimension": "Synthesis & coding practice",
            "question": "Which best describes your synthesis and coding practice for turning sessions into themes?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out how to code and synthesize—my approach changes study to study and the themes can be inconsistent."},
                {"stage": "P", "text": "I have a coding flow that works for me, but it mostly lives in my head—others wouldn’t get the same themes if they tried."},
                {"stage": "I", "text": "I use a documented coding workflow and codebook—someone else can review how codes roll up into themes."},
                {"stage": "A", "text": "Others use my coding templates and codebook structure without my help—they can produce comparable themes across studies."},
                {"stage": "S", "text": "I set standards for how we code and synthesize across the organization—I mentor and calibrate researchers to keep it consistent."},
            ]
        },
        {
            "id": "epias_l0_evidence_traceability",
            "dimension": "Evidence chains & traceability",
            "question": "Which best describes your practice for keeping research findings traceable to original evidence?",
            "options": [
                {"stage": "E", "text": "I often work from notes and memory—sometimes I can’t reliably pull the exact transcript or quote that supports a finding."},
                {"stage": "P", "text": "I keep my own breadcrumbs to support findings, but the trail is personal—someone else would struggle to follow it."},
                {"stage": "I", "text": "Each finding has a traceable evidence chain to transcripts, clips, and participant IDs—others can review it end to end."},
                {"stage": "A", "text": "I’ve created evidence-chain formats others use without me—teams can keep traceability consistent across projects."},
                {"stage": "S", "text": "I govern evidence-traceability standards for the organization—I audit work and coach teams when the chain is weak."},
            ]
        },
        {
            "id": "epias_l0_research_artifacts",
            "dimension": "Study artifacts & handoff readiness",
            "question": "Which best describes your study documentation and handoff readiness for other researchers?",
            "options": [
                {"stage": "E", "text": "It would be rough—my scripts, recruitment notes, and session tracking are patchy and I’m still learning what to document."},
                {"stage": "P", "text": "I can keep myself on track with my own docs, but they’re built for me—handoff to someone else would be slow."},
                {"stage": "I", "text": "My protocol, screener, consent, session notes, and tracking are documented and versioned—someone else could continue cleanly."},
                {"stage": "A", "text": "Others run studies using my standard study kits without my help—they stay consistent even when teams change."},
                {"stage": "S", "text": "I set organizational standards for study documentation and data handling—I train people and keep governance in place."},
            ]
        },
        {
            "id": "epias_l0_readouts_decisions",
            "dimension": "Readouts & decision linkage",
            "question": "Which best describes your research readout practice for linking findings to decisions?",
            "options": [
                {"stage": "E", "text": "My readouts are pretty ad hoc—sometimes the room leaves without clear next steps tied to the evidence."},
                {"stage": "P", "text": "I can deliver a strong readout in my own style, but it depends on me—others don’t have a repeatable way to do it."},
                {"stage": "I", "text": "I use a documented readout structure that links findings to evidence and implications—others can reuse and review it."},
                {"stage": "A", "text": "Teams use my readout templates and facilitation guides without my help—decisions consistently reference the findings."},
                {"stage": "S", "text": "I set expectations for research readouts and decision traceability across the organization—I mentor and enforce the standard."},
            ]
        },
        {
            "id": "epias_l0_quality_verification",
            "dimension": "Verification & quality checks",
            "question": "Which best describes your practice for verifying themes and running quality checks on synthesis?",
            "options": [
                {"stage": "E", "text": "I don’t have a consistent way to verify themes yet—I’m still figuring out what “good enough” checking looks like."},
                {"stage": "P", "text": "I do my own informal sanity checks, but it’s mostly solo—others don’t routinely review or challenge my synthesis."},
                {"stage": "I", "text": "I run a documented verification step—spot-check coding against transcripts and get peer review before finalizing themes."},
                {"stage": "A", "text": "Others follow my QA checklist without my help—synthesis quality stays consistent across researchers and studies."},
                {"stage": "S", "text": "I govern research quality standards for the organization—I run calibration, mentoring, and reviews to keep the bar consistent."},
            ]
        },
    ],
    1: [
        {
            "id": "epias_l1_prompt_organization",
            "dimension": "Prompt organization",
            "question": "Which best describes your prompt organization for AI-assisted research synthesis?",
            "options": [
                {"stage": "E", "text": "I mostly improvise prompts each time—I'm still figuring out what works and the results are inconsistent."},
                {"stage": "P", "text": "I keep a few favorite prompts in my own notes, but they're personal and only I use them."},
                {"stage": "I", "text": "I maintain a documented prompt set with examples and placeholders—others can review it and reuse it."},
                {"stage": "A", "text": "I run a shared prompt pack and short checklist that teammates can use without my help."},
                {"stage": "S", "text": "I set and maintain the organization’s standard prompt library, and I govern updates based on team feedback."},
            ]
        },
        {
            "id": "epias_l1_ai_judgment",
            "dimension": "AI judgment and verification",
            "question": "Which best describes your AI judgment and verification when accepting AI-generated themes or insights?",
            "options": [
                {"stage": "E", "text": "I'm still learning what to trust—I often take the AI summary at face value unless it looks obviously wrong."},
                {"stage": "P", "text": "I do a quick spot-check in the transcript when something feels off, but it's just my personal habit."},
                {"stage": "I", "text": "I follow a documented verification step—key points get checked against the transcript and recorded."},
                {"stage": "A", "text": "I built a team workflow where verification is required before anything becomes a finding, and others use it without me."},
                {"stage": "S", "text": "I set org-wide rules for verifying AI-assisted synthesis and mentor teams on applying them consistently."},
            ]
        },
        {
            "id": "epias_l1_evidence_traceability",
            "dimension": "Traceability to source material",
            "question": "Which best describes how you ensure traceability from AI-assisted findings to participant evidence?",
            "options": [
                {"stage": "E", "text": "It’s hit or miss—I don’t consistently link findings back to the exact transcript lines or quotes."},
                {"stage": "P", "text": "I can usually find the supporting quotes for myself, but I don’t package the evidence trail for others."},
                {"stage": "I", "text": "My readouts include a clear evidence trail—quotes and transcript references that others can review."},
                {"stage": "A", "text": "I provide a shared template that makes evidence chains easy for the team, so others can produce traceable readouts without me."},
                {"stage": "S", "text": "I define the organization’s evidence-chain standard and audit samples to keep traceability consistent and honest."},
            ]
        },
        {
            "id": "epias_l1_coding_consistency",
            "dimension": "Consistency in coding and themes",
            "question": "Which best describes your approach to keeping AI-assisted coding and themes consistent over time?",
            "options": [
                {"stage": "E", "text": "I keep trying different prompts and labels—my codes shift a lot and the themes feel inconsistent."},
                {"stage": "P", "text": "I have my own go-to codes and prompting style, but it mostly lives in my head and only I can apply it."},
                {"stage": "I", "text": "I maintain a documented codebook and coding guidance—others can apply it and see what changed."},
                {"stage": "A", "text": "I built a shared coding kit with examples that teammates use without my help to stay consistent."},
                {"stage": "S", "text": "I set and evolve org-level coding standards and mentor researchers on applying them across teams."},
            ]
        },
        {
            "id": "epias_l1_work_recordkeeping",
            "dimension": "Recordkeeping and reviewability",
            "question": "Which best describes the recordkeeping and reviewability of your AI-assisted research work?",
            "options": [
                {"stage": "E", "text": "They’d mostly have to start from scratch—I don’t reliably save the prompts, inputs, and outputs."},
                {"stage": "P", "text": "I can share my chat logs and a few prompts, but it usually takes my explanation to make sense of them."},
                {"stage": "I", "text": "I save prompts, inputs, and outputs in a documented place—someone else can review and rerun the step."},
                {"stage": "A", "text": "I provide a plug-and-play workspace with examples that others can use without asking me questions."},
                {"stage": "S", "text": "I standardize how AI-assisted work is recorded across the org and govern adherence through process and enablement."},
            ]
        },
    ],
    2: [
        {
            "id": "epias_l2_spec_clarity",
            "dimension": "Spec clarity",
            "question": "Which best describes your AI research spec clarity when requesting bounded deliverables?",
            "options": [
                {"stage": "E", "text": "I try a few prompts and adjust as I go — I'm still figuring out which details change the output and results can be inconsistent."},
                {"stage": "P", "text": "I can reliably get what I need by describing the study and my goals — but the spec is mostly in my head and only I can write it well."},
                {"stage": "I", "text": "I use a written spec with inputs, constraints, and an output format — it’s saved with the study so others can review what I asked for."},
                {"stage": "A", "text": "I provide spec templates and examples that other researchers fill in — they get consistent outputs without needing me to shape the request."},
                {"stage": "S", "text": "I set org-wide standards for AI research specs and teach them — we review adherence and update the standard over time."},
            ]
        },
        {
            "id": "epias_l2_chunking",
            "dimension": "Chunking & task design",
            "question": "Which best describes your chunking and task design when using AI for research analysis?",
            "options": [
                {"stage": "E", "text": "I tend to hand big chunks to AI and see what comes back — I'm still learning how to split work into bounded tasks."},
                {"stage": "P", "text": "I have my own repeatable way to break analysis into a few AI tasks — but it’s personal and not something others use."},
                {"stage": "I", "text": "I follow a documented workflow that chunks analysis into defined AI deliverables — each step has clear inputs, outputs, and a handoff back to me."},
                {"stage": "A", "text": "Other researchers run my chunked workflow as written — they can plan the breakdown and execute it without my help."},
                {"stage": "S", "text": "I standardize chunking patterns by study type and risk level across the org — I mentor teams and evolve the playbook based on outcomes."},
            ]
        },
        {
            "id": "epias_l2_integration_quality",
            "dimension": "Integration into findings",
            "question": "Which best describes how you integrate AI outputs into research findings and readouts?",
            "options": [
                {"stage": "E", "text": "I paste AI outputs into my doc and rewrite until it sounds right — the final narrative quality varies by project."},
                {"stage": "P", "text": "I have a reliable way to shape AI outputs into findings and implications — but it’s mostly my personal craft and hard to transfer."},
                {"stage": "I", "text": "I integrate AI pieces using a documented structure (finding → evidence → implication) — others can trace the readout back to source material."},
                {"stage": "A", "text": "My integration templates let other researchers produce consistent readouts from AI outputs — they don’t need me to make it coherent."},
                {"stage": "S", "text": "I define org expectations for AI-assisted findings and readouts — I coach researchers and run quality reviews to keep it consistent."},
            ]
        },
        {
            "id": "epias_l2_qa_evidence_chain",
            "dimension": "QA & evidence traceability",
            "question": "Which best describes your QA and evidence-traceability practice for AI-assisted research synthesis?",
            "options": [
                {"stage": "E", "text": "I do occasional spot checks when something feels off — I haven't found a reliable QA routine yet."},
                {"stage": "P", "text": "I regularly verify key quotes and a few claims against transcripts — but my QA steps aren’t documented and depend on me."},
                {"stage": "I", "text": "I use a documented QA checklist with a sampling plan and transcript links — the evidence chain is traceable and reviewable by others."},
                {"stage": "A", "text": "Other researchers use my QA system without my involvement — it consistently catches mismatches before findings get shared."},
                {"stage": "S", "text": "I set governance for AI-involved research QA (risk tiers, required checks, audits) — I mentor reviewers and own the standard."},
            ]
        },
        {
            "id": "epias_l2_reusability",
            "dimension": "Reusability of assets",
            "question": "Which best describes the reusability of your AI-assisted research prompts, templates, and synthesis assets?",
            "options": [
                {"stage": "E", "text": "I sometimes reuse a prompt if I can find it — most of the time I’m still improvising and starting from scratch."},
                {"stage": "P", "text": "I maintain my own prompts, templates, and codebook starters — but they’re for me and others don’t really use them."},
                {"stage": "I", "text": "I keep versioned templates, specs, and examples in a shared place — others can reuse them and see what changed and why."},
                {"stage": "A", "text": "I maintain a shared kit that researchers use without my help — it works across teams and produces consistent deliverables."},
                {"stage": "S", "text": "I steward the org’s library of AI research assets and standards — I govern updates, deprecate bad patterns, and onboard people."},
            ]
        },
    ],
    3: [
        {
            "id": "epias_l3_repeatable_synthesis",
            "dimension": "Repeatable synthesis workflow",
            "question": "Which best describes how repeatable your AI-assisted research synthesis workflow is across studies?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out the steps—each study I improvise and the results are inconsistent."},
                {"stage": "P", "text": "I have a sequence that usually works, but it lives in my head and only I can run it end-to-end."},
                {"stage": "I", "text": "The steps and checkpoints are documented and traceable, so others can review how I got from quotes to themes."},
                {"stage": "A", "text": "Teammates run the workflow without me and get comparable themes and outputs across studies."},
                {"stage": "S", "text": "I set the organization’s standard for AI-assisted synthesis workflows and govern changes and exceptions."},
            ]
        },
        {
            "id": "epias_l3_context_pack",
            "dimension": "Context engineering for research inputs",
            "question": "Which best describes your context engineering practice for preparing AI with research study inputs?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out what context it needs—I paste in whatever I have and hope it’s enough."},
                {"stage": "P", "text": "I have my own checklist for briefs, transcripts, and participant notes, but it’s personal and not shared."},
                {"stage": "I", "text": "I use a documented context pack that others can inspect—brief, participants, artifacts, and assumptions are all captured."},
                {"stage": "A", "text": "Others can fill in my context pack template and run the workflow without my help."},
                {"stage": "S", "text": "I set org-wide standards for context packs and research data handling, and I audit adherence."},
            ]
        },
        {
            "id": "epias_l3_evidence_chain",
            "dimension": "Verification and evidence chains",
            "question": "Which best describes your practice for verifying AI-generated findings with transcript evidence?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out a reliable check—I spot-check a few quotes, but I often miss gaps."},
                {"stage": "P", "text": "I have a personal way of validating support, but it’s in my head and others can’t easily follow it."},
                {"stage": "I", "text": "I require a traceable evidence chain—each code, theme, and claim links back to specific transcript segments for review."},
                {"stage": "A", "text": "Others use my verification steps and consistently produce findings with evidence links without needing my oversight."},
                {"stage": "S", "text": "I set the organization’s verification standard and review process for AI-assisted findings, and I mentor reviewers."},
            ]
        },
        {
            "id": "epias_l3_failure_recovery",
            "dimension": "Checkpointing and failure handling",
            "question": "Which best describes how you checkpoint and recover when AI-assisted synthesis goes off track?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out recovery—when it goes off track, I usually restart from scratch."},
                {"stage": "P", "text": "I can usually get it back on track, but my fixes are ad hoc and only I know what to try."},
                {"stage": "I", "text": "I have documented checkpoints and fallback steps, so anyone can pause, correct, and resume with the same artifacts."},
                {"stage": "A", "text": "The workflow guardrails let others recover from common failures without my help and still finish the synthesis."},
                {"stage": "S", "text": "I define the org’s guardrails and incident playbooks for AI-assisted research workflows, and I track recurring failures."},
            ]
        },
        {
            "id": "epias_l3_decision_ownership",
            "dimension": "Decision ownership in readouts",
            "question": "Which best describes your decision ownership practice for AI-assisted research readouts?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out what to trust—I sometimes accept AI-written findings and fix issues after the fact."},
                {"stage": "P", "text": "I make the final calls and rewrite as needed, but my decision criteria aren’t documented for anyone else."},
                {"stage": "I", "text": "My decision criteria are documented and reviewable—readout claims are tied to codes, themes, and source excerpts."},
                {"stage": "A", "text": "Others use my criteria and templates to produce readouts with clear ownership and traceability without my help."},
                {"stage": "S", "text": "I set org-wide policy for decision ownership and disclosure in AI-assisted readouts, and I govern compliance."},
            ]
        },
    ],
    4: [
        {
            "id": "epias_l4_eval_automation",
            "dimension": "Automated quality evaluation",
            "question": "Which best describes how you evaluate the quality of AI-generated research synthesis?",
            "options": [
                {"stage": "E", "text": "I do occasional spot-checks against a few quotes — results are inconsistent and I’m still figuring out what to trust."},
                {"stage": "P", "text": "I use my own mental checklist and rerun until it looks right — but it’s personal and only I apply it consistently."},
                {"stage": "I", "text": "I run documented checks with clear pass/fail criteria — outputs are traceable and others can review what passed and why."},
                {"stage": "A", "text": "The workflow runs those checks automatically and blocks weak outputs — teammates get reliable synthesis without me watching."},
                {"stage": "S", "text": "I set and govern the organization’s evaluation standards for AI-generated research outputs — and I mentor teams on meeting them."},
            ]
        },
        {
            "id": "epias_l4_evidence_chain",
            "dimension": "Evidence-chain traceability",
            "question": "Which best describes your evidence chain traceability when sharing or defending research findings?",
            "options": [
                {"stage": "E", "text": "Sometimes I can’t quickly reconstruct the exact supporting lines — I’m still figuring out a reliable evidence trail."},
                {"stage": "P", "text": "I can usually pull the supporting quotes from my own notes — but the structure is personal and others struggle to follow it."},
                {"stage": "I", "text": "Findings are linked to transcript lines, participant IDs, and codes — the evidence chain is documented and reviewable by others."},
                {"stage": "A", "text": "Anyone can click from a finding to the underlying transcript lines or clips in our system — they don’t need me to rebuild the trail."},
                {"stage": "S", "text": "I define and enforce org-wide requirements for evidence chains in research outputs — and I coach reviewers on how to audit them."},
            ]
        },
        {
            "id": "epias_l4_autonomy_monitoring",
            "dimension": "Autonomous run monitoring and recovery",
            "question": "Which best describes your autonomous research run monitoring and recovery practice?",
            "options": [
                {"stage": "E", "text": "It often stalls or drifts into messy outputs — I’m still experimenting with autonomous runs and they’re not reliable yet."},
                {"stage": "P", "text": "It can keep going if I set it up carefully — but I’m the one who monitors and fixes issues using my personal habits."},
                {"stage": "I", "text": "It runs with documented checkpoints and logs — others can review what happened, what failed, and what needs a decision."},
                {"stage": "A", "text": "It keeps running, self-checks, and alerts the right person only on exceptions — the team doesn’t need me on standby."},
                {"stage": "S", "text": "I set the org’s operating standards for autonomous research runs — including escalation, incident review, and training for operators."},
            ]
        },
        {
            "id": "epias_l4_harness_reuse",
            "dimension": "Shared research harness and reuse",
            "question": "Which best describes your shared AI-assisted research workflow and reuse practice?",
            "options": [
                {"stage": "E", "text": "I’m still piecing together tools and prompts — I don’t have a repeatable setup others can follow."},
                {"stage": "P", "text": "I have a workflow that works for me — but it lives in my head and others haven’t really adopted it."},
                {"stage": "I", "text": "The workflow is documented with inputs, outputs, and a shared codebook — others can run it and review changes."},
                {"stage": "A", "text": "I maintain a self-serve harness teammates use to process studies end-to-end — they get results without my help."},
                {"stage": "S", "text": "I set org-wide patterns for shared research harnesses — and I govern funding, ownership, and lifecycle across teams."},
            ]
        },
        {
            "id": "epias_l4_participant_data_governance",
            "dimension": "Governance for participant data and privacy",
            "question": "Which best describes your governance for participant data and privacy in AI-related research?",
            "options": [
                {"stage": "E", "text": "I make case-by-case calls and sometimes change my approach — I’m still figuring out what’s safe and consistent."},
                {"stage": "P", "text": "I follow my own rules for redaction and storage — but they’re personal and not consistently used by others."},
                {"stage": "I", "text": "We have documented steps for redaction, access, and retention per study — others can audit what was done and why."},
                {"stage": "A", "text": "The pipeline enforces redaction and access rules automatically — teams can run studies without me policing privacy."},
                {"stage": "S", "text": "I define and govern the organization’s standards for participant data in AI workflows — including reviews, exceptions, and mentoring."},
            ]
        },
    ],
    5: [
        {
            "id": "epias_l5_goal_setting",
            "dimension": "Goal-setting for autonomous UXR runs",
            "question": "Which best describes your goal-setting practice for end-to-end autonomous UX research runs?",
            "options": [
                {"stage": "E", "text": "I’m still figuring out what details the AI needs — my briefs are inconsistent and the outputs vary a lot."},
                {"stage": "P", "text": "I have a reliable way I frame goals and constraints, but it’s mostly in my head — others don’t use it without me."},
                {"stage": "I", "text": "I use documented goal briefs with clear success criteria and scope — others can review what I asked for and why."},
                {"stage": "A", "text": "I’ve built goal-brief templates and guardrails others can use to run autonomous studies — they get solid results without my help."},
                {"stage": "S", "text": "I set the organization’s standard for autonomous-research goal briefs — I mentor teams and govern changes to how goals are defined."},
            ]
        },
        {
            "id": "epias_l5_exception_oversight",
            "dimension": "Exception oversight and intervention",
            "question": "Which best describes your oversight and intervention practice for exceptions in autonomous AI-led research workflows?",
            "options": [
                {"stage": "E", "text": "I usually find problems after the readout — I’m still figuring out what to monitor and when to step in."},
                {"stage": "P", "text": "I do my own spot-checks and jump in when something feels off, but my thresholds are personal — others can’t follow the same playbook."},
                {"stage": "I", "text": "I have documented exception rules and review steps — issues and interventions are logged so others can audit the run."},
                {"stage": "A", "text": "I’ve set up monitoring and triage so teammates can handle exceptions without me — the system routes the right problems to the right person."},
                {"stage": "S", "text": "I define org-wide oversight expectations for autonomous research — I run incident reviews and set how exceptions are governed."},
            ]
        },
        {
            "id": "epias_l5_evidence_chains",
            "dimension": "Trust calibration through evidence chains",
            "question": "Which best describes your evidence-chain practice for verifying AI-generated themes against source data?",
            "options": [
                {"stage": "E", "text": "I sometimes skim transcripts when something sounds wrong — I don’t yet have a consistent way to verify themes."},
                {"stage": "P", "text": "I do my own sampling and re-check quotes against transcripts, but it’s a personal routine — the verification isn’t repeatable for others."},
                {"stage": "I", "text": "I use a documented evidence-chain process — findings link back to quotes and timestamps that others can review."},
                {"stage": "A", "text": "I’ve built a system that generates evidence maps and verification reports by default — others use it without my involvement."},
                {"stage": "S", "text": "I set the org standard for evidence chains in AI-assisted synthesis — I train teams and govern what counts as acceptable verification."},
            ]
        },
        {
            "id": "epias_l5_pipeline_adaptation",
            "dimension": "System adaptation and continuous improvement",
            "question": "Which best describes how your autonomous research systems adapt and improve after each study?",
            "options": [
                {"stage": "E", "text": "I make occasional prompt tweaks when something breaks — I’m still figuring out what changes actually improve results."},
                {"stage": "P", "text": "I refine prompts, codebooks, and checks based on my own learnings, but it’s mostly in my head — others don’t inherit the improvements."},
                {"stage": "I", "text": "Changes are versioned and documented — others can see what changed, why, and what evidence showed it worked."},
                {"stage": "A", "text": "The pipeline captures feedback and updates shared templates so teams benefit automatically — it runs without me to keep improving."},
                {"stage": "S", "text": "I govern how autonomous-research systems evolve across the org — I set review gates and mentor teams on safe improvement practices."},
            ]
        },
        {
            "id": "epias_l5_accountability",
            "dimension": "Accountability for automated research decisions",
            "question": "Which best describes how you ensure accountability for automated, end-to-end UX research decisions?",
            "options": [
                {"stage": "E", "text": "Accountability is a bit fuzzy right now — I accept most outputs unless an obvious issue shows up."},
                {"stage": "P", "text": "I personally keep notes on what I approved and why, but it’s not shared — others wouldn’t know what I signed off on."},
                {"stage": "I", "text": "Decision points and approvals are documented with traceable records — others can see who approved what and on what basis."},
                {"stage": "A", "text": "I’ve built accountability into the workflow so teams follow the same sign-off and audit trail without me — it’s the default way of working."},
                {"stage": "S", "text": "I set organizational policy for accountability in autonomous UX research — I mentor leaders and govern enforcement and escalations."},
            ]
        },
    ],
}



# ---------------------------------------------------------------------------
# Backward-compatible aliases (scorer.py imports these by name)
# ---------------------------------------------------------------------------

SAE_QUESTIONS = SAE_QUESTIONS_DESIGN
EPIAS_QUESTIONS = EPIAS_QUESTIONS_DESIGN


# ---------------------------------------------------------------------------
# Accessor functions
# ---------------------------------------------------------------------------

def get_all_sae_questions(role: str = 'design') -> list:
    """Return all SAE level identification questions for the specified role."""
    if role == 'uxr':
        return SAE_QUESTIONS_UXR
    return SAE_QUESTIONS_DESIGN


def get_epias_questions(sae_level: int, role: str = 'design') -> list:
    """Return EPIAS maturity questions for a specific SAE level and role."""
    if role == 'uxr':
        return EPIAS_QUESTIONS_UXR.get(sae_level, EPIAS_QUESTIONS_UXR.get(1, []))
    return EPIAS_QUESTIONS_DESIGN.get(sae_level, EPIAS_QUESTIONS_DESIGN.get(1, []))

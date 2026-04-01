# The Tree-Shaped Professional v3: Plan

> **Status:** Draft — 2026-03-30
> **Author:** Noah + Claude
> **Goal:** Evolve aiskillsmap from a design-specific assessment into a universal framework for any professional who uses AI.

---

## Vision

**From:** "Tree-Shaped Designer" (Design + UXR only)
**To:** "Tree-Shaped Professional" — applicable to any discipline where someone uses AI

The metaphor stays the same:

- **Roots** = your domain know-how (craft foundation)
- **Canopy width** = AI solution autonomy (how independently your AI systems operate)
- **Canopy height** = leadership in communicating those solutions & patterns (EPIAS stewardship)

---

## 1. Architecture: Separate Framework from Content

The core insight is a **three-layer architecture** that separates what we measure from how we ask about it.

### Layer 1: Framework Skeleton (domain-agnostic)

A YAML schema that defines **question slots** by their gist — the invariant thing being measured — without any domain-specific language.

```yaml
# framework_skeleton.yaml
dimensions:
  root:
    name: "Craft Foundation"
    description: "How deep is your domain expertise, independent of AI?"
    slots:
      - id: root_workflow
        gist: "How you turn ambiguous requests into concrete deliverables"
        epias_anchors:
          E: "Improvise each time, outputs vary"
          P: "Reliable personal process, in your head"
          I: "Documented, others can follow the trail"
          A: "Others run your system independently"
          S: "You set org standards and mentor adoption"
      - id: root_rationale
        gist: "How you capture and trace decision rationale"
      - id: root_quality
        gist: "How you ensure quality of your own work"
      - id: root_reuse
        gist: "How you build reusable systems/patterns from your work"
      - id: root_leadership
        gist: "How you elevate others' practice in the domain"

  sae:
    name: "AI Autonomy Level"
    description: "How much does AI do independently in your work?"
    slots:
      - id: sae_tools
        gist: "How you use AI day-to-day"
      - id: sae_qa
        gist: "How you verify AI output quality"
      - id: sae_continuity
        gist: "What happens when you step away"
      - id: sae_instruction
        gist: "How you instruct/configure AI"
      - id: sae_outputs
        gist: "What AI routinely produces for you"
      - id: sae_reuse
        gist: "Who else can use your AI setup"

  canopy:
    name: "AI Practice Maturity"
    description: "How deeply internalized is your AI practice?"
    slots_per_level:
      L1:
        - gist: "How you organize what works"
        - gist: "How you judge AI output readiness"
        - gist: "Consistency across outputs"
        - gist: "Traceability of AI-influenced decisions"
        - gist: "How you learn and improve your AI practice"
      L2:
        - gist: "How you spec bounded AI tasks"
        - gist: "How you integrate AI-produced pieces"
        - gist: "Quality assurance of assembled output"
        - gist: "Reproducibility of your specs"
        - gist: "How others adopt your approach"
      L3:
        - gist: "How you design multi-step workflows"
        - gist: "How you set and monitor checkpoints"
        - gist: "How context persists across sessions"
        - gist: "How you handle AI failures mid-workflow"
        - gist: "How you teach workflow design to others"
      L4:
        - gist: "How you define rules for autonomous systems"
        - gist: "How you monitor autonomous execution"
        - gist: "How you handle edge cases and escalation"
        - gist: "How you maintain and evolve the system"
        - gist: "How you govern autonomous AI for the org"
      L5:
        - gist: "How you set goals for fully autonomous systems"
        - gist: "How you evaluate goal attainment"
        - gist: "How you handle exceptions and drift"
        - gist: "How you ensure alignment over time"
        - gist: "How you set org-wide autonomous AI strategy"
```

The **gist** is the invariant. Everything below builds on it.

### Layer 2: Domain Content Packs

Each domain fills in the skeleton with role-specific language:

```yaml
# domains/software_engineering.yaml
domain:
  id: software_engineering
  name: "Software Engineering"
  icon: "🔧"
  related_domains: [devops, data_engineering, ml_engineering]

  root_questions:
    root_workflow:
      question: "Which best describes how you turn requirements into working code?"
      options:
        E: "I figure it out as I go — architecture and patterns vary project to project."
        P: "I have reliable patterns I follow, but they're mostly in my head."
        I: "I follow documented architecture decisions and patterns — PRs show the reasoning."
        A: "My templates, linters, and architecture docs are the team's starting point."
        S: "I set engineering standards for the org and mentor technical leads."

  sae_questions:
    sae_tools:
      question: "Which best describes how you use AI in your engineering work?"
      options:
        L0: "I don't use AI tools in my engineering work."
        L1: "I use AI for one task at a time — autocomplete, generate, debug, repeat."
        L2: "I give AI a spec and it produces working modules — I review, test, and integrate."
        L3: "I run multi-step AI workflows with test gates — work persists across sessions."
        L4: "I run autonomous AI agents that code, test, and self-correct without me present."
        L5: "AI handles my engineering workflow end-to-end — I set goals and review exceptions."
    # ... etc
```

### Layer 3: Question Bank (generated at build time, not test time)

For each domain, a small set of **seed questions** (hand-written, high quality) are used to generate a larger bank of variant questions via LLM. This happens at build time. At test time, the system picks from the pre-generated bank — no LLM calls, instant loading, deterministic scoring.

```
Skeleton gist: "How you turn ambiguous requests into concrete deliverables"

Seed (design):     "How you turn vague requests into wireframes?"
Seed (engineering): "How you turn requirements into working code?"
Seed (finance):    "How you turn business needs into financial models?"

Generated variants (finance):
  - "When a stakeholder says 'we need to understand the ROI,' how do you get to a model?"
  - "Which best describes your process for scoping a financial analysis from unclear inputs?"
  - [10 more variants, human-reviewed]
```

**Result:** Each person sees slightly different questions. No two retakes are identical. But scoring is always against the same EPIAS anchors.

---

## 2. User Experience Flow

### Step 0: Intake (~30 seconds)

```
What world do you work in? Pick all that apply:

[ ] Product Design      [ ] Software Engineering    [ ] Data Science
[ ] UX Research          [ ] Marketing               [ ] Finance
[ ] Content Strategy     [ ] Operations              [ ] Project Management
[ ] Education            [ ] Healthcare              [ ] Legal
[ ] Other: ________
```

**If 1 domain selected:** Use that domain's question bank.

**If 2+ domains selected:** Offer a choice:

> "Answer about each area separately (thorough, ~15min)"
> OR
> "Answer in general terms across your work (~8min)"

This directly addresses the "my work doesn't fit one thing" feedback. People who span design + research can either:
- Take a **multi-domain assessment** → get a tree per domain (a *grove*)
- Take a **generalist assessment** → domain-neutral questions from the skeleton gists

### Step 1: Root Questions — 5 questions

Domain-specific or generalist, drawn from the question bank. Measures E→P→I→A→S at L0 (craft foundation depth).

### Step 2: SAE Questions — 6 questions

AI autonomy level. Already nearly domain-agnostic. Light domain flavor via bank variants.

### Step 3: Canopy Questions — 5 questions

Only shown if SAE > 0. Domain-flavored EPIAS questions for the detected SAE level.

**Total: 11–16 questions.** Same as current v2. Not longer.

### Step 4: Results + Growth Path + New Features

1. **Your Tree** — species, root/canopy balance, growth narrative
2. **Your Growth Path** — concrete next steps for your specific cell
3. **Continue the Conversation** — AI prompt export (see Section 4)
4. **Help Us Improve** — feedback gate (see Section 5)

---

## 3. Question Generation Pipeline

Build-time process. No user-facing LLM calls.

```
Phase 1: Framework Skeleton
  ├── 5 root gists
  ├── 6 SAE gists
  └── 5×5 canopy gists (per SAE level)
  → Hand-written, universal, reviewed by Noah

Phase 2: Seed Questions (per domain)
  ├── 2–3 hand-written questions per gist per domain
  ├── Written by domain experts or carefully prompted
  └── These are the "gold standard" — quality over quantity
  → Output: ~15–20 seed questions per domain

Phase 3: Question Bank Generation (LLM-assisted, build-time)
  ├── For each seed question, generate 5–10 variants
  ├── Vary: framing, specificity, vocabulary
  ├── Constraint: same EPIAS anchors, same gist, same scoring
  ├── Human review pass to cull bad variants
  └── Mark each: quality_score, reviewed (true/false)
  → Output: question_bank/{domain}.yaml

Phase 4: Generalist Questions
  ├── Derived from skeleton gists directly
  ├── No domain-specific language
  ├── "In your work..." instead of "In your design work..."
  └── One canonical set + variants
  → Output: question_bank/generalist.yaml
```

Only `reviewed: true` questions enter the live bank.

---

## 4. AI Continuation Prompt

After results, offer a copy-paste prompt for the user's own AI assistant:

> **Want to go deeper?**
> Copy this prompt and paste it into ChatGPT, Claude, or any AI assistant for a personalized follow-up:

The generated prompt includes:
- Framework summary (tree metaphor, three dimensions)
- Their specific scores (e.g., Root: Practitioner, SAE: L2, Canopy: Integrator)
- Their tree species and what it means
- Their growth path recommendations
- Instructions for the AI:

```
"You are a professional development coach using the Tree-Shaped Professional
framework. The person you're speaking with just completed an assessment.
Here are their results: [scores]. Ask them 5 follow-up questions about their
specific work to give more targeted advice. Focus on [their weakest dimension].
Help them identify one concrete action they can take this week."
```

**Why this works:**
- No LLM cost on our infrastructure
- People get personalized depth
- The framework spreads — their AI learns the tree model
- Low effort for us, high perceived value for them

---

## 5. Feedback Collection Redesign

### Problem

- v1: Corner widget on every page → ~0 submissions
- v2: About page form → ~0 submissions
- People don't give feedback when they aren't asked assertively at the right moment.

### Solution: Post-Results Feedback Gate

Appears between results and share/export — the moment of peak engagement.

```
┌─────────────────────────────────────────────────┐
│  Before you go — help shape the next version     │
│                                                   │
│  How well did the questions reflect               │
│  your actual work?                                │
│  ☆ ☆ ☆ ☆ ☆                                       │
│                                                   │
│  What didn't fit? (optional)                      │
│  [________________________________________]       │
│                                                   │
│  ─── or ───                                       │
│                                                   │
│  📅 15-min feedback call → $10 gift card           │
│  [Schedule on Calendly]                           │
│                                                   │
│  [Skip and continue →]                            │
└─────────────────────────────────────────────────┘
```

**Design principles:**
- Star rating = zero friction, captures signal from everyone
- Free text = optional, captures specifics from motivated people
- Calendly + incentive = captures depth from invested people
- "Skip" always visible — no dark patterns
- Feedback linked to their assessment result (tree coordinates, domain, question IDs)

### Data stored:

```python
{
    "fit_rating": 4,                # 1-5 stars (null if skipped)
    "free_text": "...",             # optional
    "calendly_clicked": False,
    "domain": "software_engineering",
    "tree_key": "r3_c2_h1",        # links to their result
    "question_ids": [...]           # which variants they saw
}
```

---

## 6. Data Model Changes

### New structures:

```python
# Domain registry (loaded from YAML at startup)
{
    "id": "software_engineering",
    "name": "Software Engineering",
    "question_bank_path": "question_bank/software_engineering.yaml",
    "active": True
}

# Question bank entry
{
    "id": "se_root_workflow_v3",
    "slot": "root_workflow",            # maps to skeleton gist
    "domain": "software_engineering",
    "question": "Which best describes...",
    "options": [...],
    "quality_score": 4.2,
    "reviewed": True,
    "variant_of": "se_root_workflow_v1" # seed it derived from
}

# Assessment result (v3)
{
    # existing v2 fields preserved
    "version": 3,
    "domains": ["software_engineering", "data_science"],
    "assessment_mode": "multi_domain | generalist",
    "question_ids": ["se_root_workflow_v3", ...],
    "feedback": {
        "fit_rating": 4,
        "free_text": "...",
        "calendly_clicked": False
    }
}
```

### Migration path:

- v1 results (150+) → keep in `assessment_results`, read-only
- v2 results (SXSW cohort) → keep in `tree_results`, read-only
- v3 results → new `tree_results_v3` collection
- Forest visualization shows all versions (species mapping is stable across versions)

---

## 7. What Stays the Same

- **Tree metaphor** — roots, canopy width, canopy height
- **EPIAS stages** — E→P→I→A→S progression
- **SAE levels** — L0→L5 autonomy scale
- **Tree species** — 30 species mapped to (root, SAE) coordinates
- **Scoring** — median-based, deterministic
- **Forest visualization** — SVG organisms, cohort views
- **No gen-AI at test time** — all questions pre-generated
- **L0 = strength, not deficit** — the mycorrhizal fungi framing

---

## 8. Implementation Phases

### Phase 1: Framework & Content Architecture

No code changes. Pure content work.

- [ ] Finalize `framework_skeleton.yaml` with all gists and EPIAS anchors
- [ ] Write generalist question set (domain-neutral, from skeleton gists)
- [ ] Write seed questions for 3 pilot domains:
  - Design (port existing v2 questions)
  - Software Engineering (new)
  - One non-tech domain: Education or Marketing (new)
- [ ] Build question generation pipeline script (LLM at build time → YAML output)
- [ ] Human review pass on all generated questions

### Phase 2: Multi-Domain Assessment Flow

- [ ] Domain selector intake page
- [ ] Question bank loader (replaces hardcoded Python dicts)
- [ ] Generalist mode (domain-neutral questions)
- [ ] Multi-domain mode (sequential assessments per domain)
- [ ] Updated scoring for v3 data model
- [ ] Grove visualization for multi-domain results

### Phase 3: AI Continuation Prompt

- [ ] Prompt template that interpolates results
- [ ] Copy-to-clipboard button on results page
- [ ] Include framework context, scores, species, and follow-up instructions

### Phase 4: Feedback Redesign

- [ ] Post-results feedback gate UI (stars + text + Calendly)
- [ ] Set up Calendly link with gift card flow
- [ ] Link feedback to assessment result in Firestore
- [ ] Update admin dashboard for new feedback data

### Phase 5: Polish & Launch

- [ ] Update About/Framework pages for multi-domain framing
- [ ] Update forest visualization for mixed-domain cohorts
- [ ] SEO/sharing: domain-specific OG tags ("See my Tree-Shaped Engineer")
- [ ] Analytics: domain distribution, feedback rates, AI prompt copy events
- [ ] Migrate designintech.report link if URL changes

---

## 9. Open Questions

1. **How many domains at launch?** Pilot with 3–5, or go wide with 10+? More domains = more content to curate but wider reach.

2. **Grove visualization for multi-domain people?** Show 2–3 trees side by side? Overlay them? New species for hybrid professionals?

3. **Question bank size per domain?** 50 minimum? 200? Balance variety vs. quality control burden.

4. **Calendly feedback budget?** At $10/person, 50 calls = $500. Worth it for 3 months of iteration?

5. **Domain expert contributors?** Recruit domain experts to write/review seed questions for their field — community contribution model.

6. **Framework versioning?** If the skeleton evolves (new gists, changed anchors), tag assessments with `framework_version` for longitudinal comparison.

7. **URL and branding?** Keep `aiskillsmap.noahratzan.com`? Or rebrand for the broader audience?

---

## Appendix A: Current State (v2)

For reference, the current v2 assessment:

- **Domains:** Design, UX Research (hardcoded in `assessment/questions.py`)
- **Questions:** 66 total (6 SAE × 2 roles + 30 EPIAS × 2 roles + 10 root × 2 roles)
- **Scoring:** Median-based → root_depth, canopy_width (SAE), canopy_height (EPIAS)
- **Visualization:** 30 tree species, SVG organisms, forest view
- **Storage:** Firestore (`tree_results` collection)
- **Live at:** aiskillsmap.noahratzan.com (Cloud Run, `dit-maeda` service)
- **Linked from:** designintech.report

## Appendix B: Key Principle

> "An S-Steward at L1 is more valuable than an E-Explorer at L4. Depth of judgment beats breadth of tooling."

> "You can't grow a Redwood canopy on Birch roots. Go deep before you go wide."

The assessment should always reinforce this. The tree metaphor does it naturally — a huge canopy on shallow roots is visibly unstable. The scoring, results narrative, and growth paths should all point people toward deepening roots alongside extending their canopy.

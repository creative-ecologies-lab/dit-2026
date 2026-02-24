# Think-Aloud Protocol Report

**Protocol:** v2.0 (10) | **Sessions:** 10 | **Avg NPS:** 6.2 | **NPS Std Dev:** 2.25 | **Pages/session:** 13.7

## Persona Coverage
- agency_creative_director: 1 sessions
- ai_native_engineer: 1 sessions
- app_builder: 1 sessions
- career_changer: 1 sessions
- curious_explorer: 1 sessions
- daily_user: 1 sessions
- design_leader: 1 sessions
- student_non_designer: 1 sessions
- traditional_craftsperson: 1 sessions
- ux_researcher: 1 sessions

## SUS Scores (System Usability Scale)
**Overall:** 68.5 (Grade B) | **Std Dev:** 18.5 | **Range:** 65.0 pts | **vs Benchmark (68):** above

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| career_changer | 25.0 | F | 25.0-25.0 |
| student_non_designer | 55.0 | C | 55.0-55.0 |
| traditional_craftsperson | 62.5 | C | 62.5-62.5 |
| ux_researcher | 65.0 | C | 65.0-65.0 |
| app_builder | 72.5 | B | 72.5-72.5 |
| agency_creative_director | 75.0 | B | 75.0-75.0 |
| design_leader | 75.0 | B | 75.0-75.0 |
| ai_native_engineer | 82.5 | A | 82.5-82.5 |
| daily_user | 82.5 | A | 82.5-82.5 |
| curious_explorer | 90.0 | A+ | 90.0-90.0 |

## Nielsen Heuristic Analysis
**Coverage:** 9/10 heuristics cited | **Citation rate:** 97%

| Heuristic | Count |
|-----------|-------|
| Match Real World | 70 |
| Visibility Of System Status | 39 |
| Recognition Over Recall | 21 |
| User Control Freedom | 4 |
| Flexibility Efficiency | 4 |
| Help Documentation | 3 |
| Consistency Standards | 3 |
| Minimalist Design | 2 |
| Error Prevention | 1 |

**Missing:** error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 210 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 24% |
| Notices Correct Action | 54% |
| Associates Action With Goal | 64% |
| Sees Progress | 12% |

### assess?cohort=think-aloud-test (163 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, will_try_right_effect, sees_progress
  Archetypes: student_non_designer, traditional_craftsperson, ai_native_engineer, curious_explorer, agency_creative_director, career_changer, app_builder, ux_researcher, daily_user, design_leader
  - [student_non_designer] associates_action_with_goal: Here's where it breaks down for me: I don't know if this intake data is *used* somewhere in the study design or if it's just metadata. As an academic, I want to know—does demographic data actually affect the task or interface I'm about to interact with? That's not communicated. It feels like busywork unless I understand the purpose.
  - [student_non_designer] associates_action_with_goal: Here's where I'm stuck: 'automation level' is ambiguous to me. In my ML work, automation could mean model inference speed, training pipeline orchestration, or code generation. Without seeing the options, I don't know if this is asking about my *use* of AI tools, or the *design* of automated systems. The terminology doesn't map cleanly to how I think about my work.
  - [student_non_designer] notices_correct_action: I can't assess if I can find the 'right' option until I see what the automation levels actually are. Without seeing the choices, I'm flying blind.

### results (32 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, will_try_right_effect, sees_progress
  Archetypes: student_non_designer, ai_native_engineer, agency_creative_director, curious_explorer, career_changer, app_builder, ux_researcher, design_leader
  - [student_non_designer] will_try_right_effect: I don't have a clear mental model yet of what 'results' means in the context of design thinking. In academia, results usually mean quantified outcomes—but I don't know what was being measured here.
  - [student_non_designer] notices_correct_action: Without understanding what the page is showing me, I can't identify what action I should take next. Are there buttons? Is this informational only? Do I need to click something to explore the growth path, or is it already displayed?
  - [student_non_designer] associates_action_with_goal: My goal is to understand how designers adopt AI tools—but I don't yet see how this results page connects to that inquiry. Is this showing me a designer's profile? My own assessment? The relationship between those two things isn't obvious.

### home (15 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, will_try_right_effect, sees_progress
  Archetypes: student_non_designer, agency_creative_director, career_changer, ux_researcher, daily_user, design_leader
  - [student_non_designer] associates_action_with_goal: Here's where I hesitate: the page doesn't clearly communicate *what* I'm assessing or *why*. The label might say 'Start Assessment' or similar, but context about the assessment's purpose — especially relevant to my research on AI adoption in design — is unclear to me right now. I'm clicking somewhat blind.
  - [ux_researcher] sees_progress: This is where I'm uncertain—I don't yet know if the tool provides transparent progress tracking, methodology explanation, or if it just launches into questions. Without seeing the page, I can't assess whether the UX communicates *how* the assessment works or just *that* it works.
  - [design_leader] will_try_right_effect: I can't see the accessibility tree, so I'm flying blind on what's actually on this page. I need to know: Is there a clear CTA? Is the assessment self-evident? Without that, I'm hesitant to proceed.

## Behavioral Realism
**Events/session:** 47.9 | **Total events:** 479

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| career_changer | 78 | 0.372 |
| ux_researcher | 65 | 0.039 |
| student_non_designer | 60 | 0.36 |
| design_leader | 55 | 0.086 |
| traditional_craftsperson | 48 | 0.164 |
| curious_explorer | 39 | 0.272 |
| agency_creative_director | 38 | 0.098 |
| daily_user | 36 | 0.109 |
| ai_native_engineer | 33 | 0.056 |
| app_builder | 27 | 0.022 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (129 mentions)
  Heuristics: match_real_world (70), visibility_of_system_status (24), recognition_over_recall (18), user_control_freedom (4), flexibility_efficiency (3), help_documentation (2), consistency_standards (2), clarity_specificity (1), clarity_and_precision (1), minimalist_design (1), clarity_standards (1), clarity_of_language_and_match_real_world (1), error_prevention (1)
- Strength: The cohort field is auto-populated from the URL, which is smart—reduces friction. The form doesn't bombard me with required fields. Weakness: It's unclear whether clicking 'Skip' will let me do the assessment at all, or if it'll exclude me from data. As someone who thinks systematically, I want to know the path dependency. But the form doesn't explain the consequences of skipping.
- The scale is well-structured and uses concrete examples (ChatGPT, Midjourney, Bolt, eval suites) which aids recognition over recall. However, the examples assume a design context—terms like 'Bolt' and 'Framer' are design-specific tools I had to infer, and 'design work' appears in every option. A strength: the progression is logical and granular. A weakness: it doesn't acknowledge that 'design work' and 'code work' might have different AI automation patterns. For someone like me (coder, not designer), the vocabulary creates a small mapping burden.
- The options themselves are well-written and progressively complex. They move from 'none' → 'manual' → 'checklist' → 'lightweight structure' → 'fully automated' → 'self-healing.' That's a logical progression. The language is technical enough that I can map my work onto it. Strength: clarity. Potential weakness: assumes the respondent already uses AI in their work — might alienate people who picked option 0.

### reflection (34 mentions)
- No onboarding or context about what 'DIT' is or who this assessment targets—I assumed it was for designers and felt like an outsider the entire time
- Repeated use of 'automation level' as a question label when the actual construct being measured shifts (tool usage → QA patterns → prompt engineering → output autonomy)—the options were clear but the headers created cognitive friction
- Results page lacks explanatory context—I couldn't tell if SAE L3 / EPIAS E was a good outcome, what it meant, or how I compare to the reference population

### home (12 mentions)
  Heuristics: visibility_of_system_status (8), help_documentation (1), recognition_over_recall (1), flexibility_efficiency (1), consistency_standards (1)
- The navigation structure is clean, but there's no contextual help for a first-time visitor. No tagline under 'DIT', no tooltip, no 'What is this?' link. For someone high in openness but new to the domain, I need scaffolding. The assessment CTA is inviting, but without understanding what I'm assessing *or* what framework I'm being assessed against, it feels premature to click it.
- Strength: clear navigation and dual CTAs reduce friction. Potential weakness: no value proposition visible above the fold—I have to trust that clicking will reveal something worth my time. For a persona like me who distrusts generic AI evals, this is a minor credibility hit. A one-sentence differentiator ('Built on agent orchestration patterns' or 'Not another prompt-ranking tool') would anchor my decision faster.
- The navigation labels are clear, but there's an information hierarchy issue: I can see two CTAs ('Take the Assessment' and 'Start Chatting'), but without understanding the framework first, I don't know which path is appropriate or what the difference is between them. The Framework link should probably be more visually prominent or the landing content should explain the context before asking for action. Right now, I'm forced to choose between two paths without enough context.

### results (10 mentions)
  Heuristics: visibility_of_system_status (7), recognition_over_recall (2), minimalist_design (1)
- Major issue: without the accessibility tree, I can't see the results content itself. But based on the available buttons and my persona, there's a visibility_of_system_status problem. A results page should clearly show: (1) my score/placement, (2) what it means, (3) how I compare to the cohort, (4) suggested next steps. The buttons exist, but if the actual results narrative is unclear or uses design-specific terminology without explanation, I'll be lost. For someone like me, this needs scaffolding—definitions, mapping to concepts I understand.
- The visibility_of_system_status is completely broken. I completed an assessment (clicked through those option items), I'm on a /results page, but I cannot see what my results actually ARE. The buttons exist (Download, Chat, Heatmap) but they're orphaned—I have no context for what they operate on. This violates the basic contract of results pages.
- Critical issue: The main results content is not visible to me. This violates 'visibility_of_system_status'—I cannot see where I stand in the framework, what my profile means, or what growth paths are available. The button labels suggest rich content exists ('Chat About Your Results', 'View Cohort Heatmap'), but the results themselves appear hidden. In fintech UX, this would be a hard blocker for user confidence.

## Question Confusion Analysis

**option-item[value='P']** (20 confusion signals)
  Archetypes affected: student_non_designer, traditional_craftsperson, curious_explorer, career_changer, app_builder
  - I need to map my actual experience to these stages. As a 2-year CS grad student in academia: I definitely don't 'start over blindly' (E) — I understan
  - Relief, actually. Once I stopped trying to interpret 'maturity stage' as a design-specific term and recognized it as a competency framework (which IS 
  - I realize I was overthinking the domain-specificity. The assessment framework itself is actually language-agnostic if you translate it: E=trial-and-er

**option-item[value='1']** (15 confusion signals)
  Archetypes affected: agency_creative_director, curious_explorer, career_changer, ux_researcher, design_leader
  - I need to map my *actual* practice to these options. I use AI for synthesis (writing, pattern-finding in transcripts, early ideation). I do NOT deploy
  - Mild frustration mixed with intellectual curiosity. The assessment is clearly designed for product/design/engineering roles, not research. I'm also no
  - I'm torn between option 1 and option 2. As a junior (0 years experience), I'm definitely NOT doing everything manually — I want to use AI! But I'm als

**option-item[value='I']** (13 confusion signals)
  Archetypes affected: student_non_designer, agency_creative_director, curious_explorer, app_builder, ux_researcher
  - I need to honestly assess my current workflow. In academia, I train models and write code for research. I do have checkpoints (validation splits, git 
  - I realize I've been overthinking 'maturity.' This isn't judging me as a person or even as a researcher — it's asking about my process discipline. As s
  - The question label 'Pick the maturity stage that best describes HOW you work' is ambiguous without context. For someone unfamiliar with design/AI matu

**option-item[value='0']** (7 confusion signals)
  Archetypes affected: curious_explorer, career_changer, traditional_craftsperson
  - I'm selecting option 0: 'I don't use AI tools — all my design work is manual.' This is unambiguous and honest. I've spent 15 years building craft thro
  - The visual hierarchy and labeling are clean. I can scan each option in sequence without confusion. The fact that none are pre-selected (selected: fals
  - Frustrated and slightly defensive. This feels like I'm being asked to fit into a box designed for a different profession. I'm not *resistant to AI* be

**option-item[value='2']** (5 confusion signals)
  Archetypes affected: student_non_designer, ux_researcher
  - There's relief here. This question *finally* maps to something concrete in my experience — I can actually answer this based on real work patterns, not
  - This question is about AI *prompting* automation level — a specific skill axis. The options scale from 'I don't write prompts' (0) through 'I engineer
  - The question asks about 'automation level' and 'MY work,' but the actual options are all about prompt reuse and AI workflow infrastructure. There's a 

**#intakeRole** (5 confusion signals)
  Archetypes affected: agency_creative_director, traditional_craftsperson
  - I see a cohort field already populated with 'think-aloud-test' — that's good, it means I didn't have to type it. The form has Age and Role fields visi
  - The form is presented as optional, but there's no clear indication of which fields are actually required versus truly optional—no visual distinction l
  - This is an intake form, but the visual design doesn't telegraph that clearly. No headline, no visual hierarchy between 'optional demographics' and the

**option-item[value='A']** (3 confusion signals)
  Archetypes affected: traditional_craftsperson
  - The accessibility tree is unavailable — I can't see the actual page layout, typography, or visual hierarchy. As a visual designer, this is frustrating
  - I need to read each option carefully — this is how I work. I don't skim. The question asks 'HOW you work,' which is asking me to self-assess my maturi
  - I'm realizing I hesitate between 'A' and 'S' because I'm genuinely uncertain whether I've reached 'systemic' influence or if that's overselling it. In

**#intakeAge** (2 confusion signals)
  Archetypes affected: career_changer, student_non_designer
  - Strength: The cohort field is auto-populated from the URL, which is smart—reduces friction. The form doesn't bombard me with required fields. Weakness
  - The form lacks context and visibility of system status. I don't know what this assessment measures, how long it will take, or what the purpose is. For

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| career_changer | 6.0 | 6-6 | 100% |
| design_leader | 6.0 | 6-6 | 100% |
| agency_creative_director | 7.0 | 7-7 | 100% |
| ai_native_engineer | 7.0 | 7-7 | 100% |
| app_builder | 7.0 | 7-7 | 100% |
| daily_user | 7.0 | 7-7 | 100% |
| student_non_designer | 7.0 | 7-7 | 100% |
| traditional_craftsperson | 7.0 | 7-7 | 100% |
| curious_explorer | 8.0 | 8-8 | 100% |

## Flow Completion
- Completion rate: 90% (9/10)

## Self-Consistency Convergence
**Overall convergence rate:** None
**Archetypes analyzed:** 0


## Notable Self-Awareness Moments
- **student_non_designer**: This is a good moment to acknowledge: I *can* code and build models, but I'm clearly outside my expertise zone here. I'm treating this like I'd approach a new academic paper — read the methodology first, *then* engage with the empirical part. I should lean into that strength rather than pretending I already know design terms.
- **student_non_designer**: I'm realizing I have no idea what 'framework' refers to on this site—I clicked that nav link earlier out of curiosity but didn't absorb what it was about. This intake form is probably context-specific, and I'm walking in somewhat blind. That's fine for a research subject, but it means I might misinterpret questions later if they reference domain concepts I don't know yet. I should just proceed honestly rather than pretending familiarity.
- **student_non_designer**: I just realized: this survey is probably aimed at designers, but I'm answering as a CS researcher. The question assumes 'design work,' but my work is code and model training. Option 3 still fits because I do use AI in iterative, checkpointed workflows—but I'm mapping it from a different domain. I should be honest about that mapping uncertainty, but the option is still the closest fit. I'm also aware that I skipped over options 1–2 quickly because they felt less technical; I gravitate toward the 'advanced AI usage' framing.
- **student_non_designer**: I'm realizing that 'automation level' in design contexts probably means something different than what I'm interpreting. But in my academic work, I genuinely do maintain lightweight evaluation systems and explicit gates. I'm not claiming to have production-grade eval suites or self-correcting loops. Option 3 is honest about where I actually am — structured but still hands-on.
- **student_non_designer**: I realize this assessment is designed for people who work with LLMs regularly. My 2 years are in academic research, not industry deployment, so my automation complexity is lower than someone building production systems. That's OK—the scale accommodates that. But I'm also aware that 'engineering context blocks' (option 3) might be inflating my own perception. I do this, but it's not as formalized as a professional prompt engineer would do it. I'm being honest about my actual practices, not aspirational.
- **student_non_designer**: I just realized: this assessment might be designed for designers, not engineers. The language—'ideas,' 'copy drafts,' 'visual concepts'—is design-native. I'm retrofitting my engineering practice onto a design framework. That's intellectually interesting (it shows the frameworks *can* generalize), but it also means I'm not the target user. My high technical skill doesn't help me here; if anything, it makes me overthink the mapping.
- **student_non_designer**: I'm realizing my workflow is much more structured than a casual AI user but nowhere near production-grade. I *do* maintain templates — literally Python notebooks with prompt structures, few-shot examples, and constraint annotations. That's what option 2 describes. I'm not maintaining shared libraries across teams (option 3), and I'm definitely not building infrastructure for others (option 4+). This is honest self-assessment, not imposter syndrome, just accurate scope.
- **student_non_designer**: I realize I've been overthinking 'maturity.' This isn't judging me as a person or even as a researcher — it's asking about my process discipline. As someone who codes and trains models, I *do* have implicit reliability practices, but I've never articulated them in the structured way these options suggest. That's interesting: the assessment is pushing me to formalize something I do intuitively. Also, my earlier clicks (bouncing between values 1, 2, 3) suggest I was genuinely confused by the question frame, not just the terminology.
- **student_non_designer**: I realize I'm reading this through a testing/CI-CD lens, not a 'design maturity' lens. That's probably the right instinct for my work, but it also means I might be missing what this assessment is *really* asking about. The term 'context' here — does it mean prompt context? Model context windows? Design system context? I'm assuming the former, but I should stay grounded in what I actually do: write prompts, test outputs, iterate. That's honest.
- **student_non_designer**: I realize I was overthinking the domain-specificity. The assessment framework itself is actually language-agnostic if you translate it: E=trial-and-error, P=pattern recognition, I=formalized knowledge, A=collaborative systems, S=institutional design. Those map to programming concepts I already know. My confusion earlier was about the word 'maturity stage,' not the underlying concept. I'm comfortable with the actual cognitive content here.

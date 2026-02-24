# Think-Aloud Protocol Report

**Protocol:** v2.1 (10) | **Sessions:** 10 | **Avg NPS:** 5.8 | **NPS Std Dev:** 0.63 | **Pages/session:** 13.9

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
**Overall:** 57.8 (Grade C) | **Std Dev:** 13.3 | **Range:** 37.5 pts | **vs Benchmark (68):** below

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| traditional_craftsperson | 40.0 | D | 40.0-40.0 |
| career_changer | 42.5 | D | 42.5-42.5 |
| daily_user | 47.5 | D | 47.5-47.5 |
| ux_researcher | 50.0 | D | 50.0-50.0 |
| student_non_designer | 52.5 | C | 52.5-52.5 |
| agency_creative_director | 57.5 | C | 57.5-57.5 |
| curious_explorer | 67.5 | C | 67.5-67.5 |
| design_leader | 70.0 | B | 70.0-70.0 |
| ai_native_engineer | 72.5 | B | 72.5-72.5 |
| app_builder | 77.5 | B | 77.5-77.5 |

## Nielsen Heuristic Analysis
**Coverage:** 6/11 heuristics cited | **Citation rate:** 101%

| Heuristic | Count |
|-----------|-------|
| Recognition Over Recall | 52 |
| Help Documentation | 31 |
| Visibility Of System Status | 28 |
| Accessibility Structure | 8 |
| Match Real World | 7 |
| User Control Freedom | 3 |

**Missing:** consistency_standards, error_prevention, flexibility_efficiency, minimalist_design, error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 265 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 15% |
| Notices Correct Action | 54% |
| Associates Action With Goal | 74% |
| Sees Progress | 17% |
| Understands Page Structure | 55% |

### assess?cohort=think-aloud-test (204 failures)
  Questions failed: sees_progress, notices_correct_action, understands_page_structure, will_try_right_effect, associates_action_with_goal
  Archetypes: ai_native_engineer, student_non_designer, design_leader, career_changer, curious_explorer, app_builder, agency_creative_director, traditional_craftsperson, ux_researcher, daily_user
  - [traditional_craftsperson] will_try_right_effect: I can't see the page structure or content at all. Without knowing what's actually displayed, I can't assess whether I'd know what action to take. This feels like being asked to critique a design I can't see.
  - [traditional_craftsperson] notices_correct_action: No visual information available. I don't know if there's a 'skip' button, a form, a dropdown, or anything else. A meticulous designer like me needs to *see* the craft before commenting on it.
  - [traditional_craftsperson] associates_action_with_goal: You've told me the page is an 'intake' with optional demographics, but without seeing the actual labels and buttons, I can't tell if the interface language matches that stated purpose.

### home (32 failures)
  Questions failed: sees_progress, notices_correct_action, understands_page_structure, will_try_right_effect, associates_action_with_goal
  Archetypes: ai_native_engineer, student_non_designer, career_changer, curious_explorer, app_builder, agency_creative_director, traditional_craftsperson, daily_user
  - [traditional_craftsperson] will_try_right_effect: The tree is missing entirely. I have no map of what's on this page—no landmarks, no structure. I'd be clicking blind. That goes against every principle I've built my career on: intentional, informed action.
  - [traditional_craftsperson] notices_correct_action: Without the accessibility tree or visual design rendered, I can't see where the self-assessment entry point is. Is it a button? A link? A form? The absence of information makes me hesitant.
  - [traditional_craftsperson] associates_action_with_goal: My goal is to take a self-assessment, but I don't know what on this page actually does that. The framing feels vague—'AI design assessment'—and vague framing usually means unclear UX underneath.

### results (29 failures)
  Questions failed: sees_progress, notices_correct_action, understands_page_structure, will_try_right_effect, associates_action_with_goal
  Archetypes: ai_native_engineer, student_non_designer, design_leader, curious_explorer, app_builder, agency_creative_director, traditional_craftsperson, ux_researcher, daily_user
  - [traditional_craftsperson] notices_correct_action: Without seeing the page, I can't confirm whether the CTAs are obvious or buried. In my experience, 'growth path suggestions' can be vague—is there a clear way to engage with them, or just decorative text?
  - [traditional_craftsperson] associates_action_with_goal: The label 'growth path suggestions' is generic. I need to see whether these suggestions actually map to *my* results or if they're just templated advice. That disconnect happens often in digital tools.
  - [traditional_craftsperson] understands_page_structure: I'm skeptical that a results page is well-structured without seeing it. Most assessment tools bury the headline result under filler. I'll need to hunt for the main takeaway and distinguish it from the fluff around it.

## Behavioral Realism
**Events/session:** 42.5 | **Total events:** 425

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| career_changer | 63 | 0.372 |
| design_leader | 61 | 0.086 |
| student_non_designer | 58 | 0.36 |
| traditional_craftsperson | 58 | 0.164 |
| curious_explorer | 42 | 0.272 |
| ux_researcher | 39 | 0.039 |
| agency_creative_director | 35 | 0.098 |
| daily_user | 30 | 0.109 |
| app_builder | 21 | 0.022 |
| ai_native_engineer | 18 | 0.056 |

## Accessibility Analysis (v2.1)
**Structure understanding rate:** 45% | **Accessibility rating:** 3/5 | **Accessibility thoughts:** 127

| Page | Structure Understanding |
|------|----------------------|
| assess?cohort=think-aloud-test | 50% |
| home | 12% |
| results | 11% |

| Archetype | Accessibility Rating |
|-----------|---------------------|
| agency_creative_director | 2/5 |
| app_builder | 2/5 |
| ux_researcher | 2/5 |
| ai_native_engineer | 3/5 |
| daily_user | 3/5 |
| design_leader | 3/5 |
| traditional_craftsperson | 3/5 |
| career_changer | 4/5 |
| curious_explorer | 4/5 |
| student_non_designer | 4/5 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (109 mentions)
  Heuristics: recognition_over_recall (51), help_documentation (27), visibility_of_system_status (19), match_real_world (7), user_control_freedom (3), accessibility_structure (1)
- The 'Skip to questions' button is valuable—it respects my autonomy and acknowledges that demographics are optional. That's good design. However, I notice the role field has a placeholder ('e.g. Product Designer, Engineer, Researcher, Student') that lists common tech roles but *doesn't* include 'Visual Designer' or 'Branding Designer' as examples. This is a minor but telling detail: the system seems oriented toward tech/product roles, not craft-focused designers like me. It's not wrong, but it's not quite meeting me where I am.
- The recognition_over_recall heuristic is strong here. Each option is fully spelled out with concrete examples (ChatGPT, Midjourney, IDE, agent harnesses). I don't have to remember what 'Level 2' means because it's right there. As someone who reads carefully and values precision, I appreciate that I'm not asked to guess or infer. The aria-labels also confirm that screen readers will get the full text, not truncated versions.
- The options are clearly labeled and each has an aria-label, which is good. But the scale assumes a user journey from 'no AI' to 'fully automated AI systems'—it doesn't account for someone who uses *other kinds* of automation (production pipelines, asset management, etc.) without AI. The question conflates 'automation level' with 'AI governance level.' For someone who's skeptical of AI but might use other tools, this creates a false equivalence. A better design would ask two separate questions: 'Do you use AI in your work?' and separately, 'What's your automation/tooling approach?' This is a **match_real_world** failure—the question structure assumes all 'automation' is AI-based.

### reflection (40 mentions)
- Visibility of system status failure: No visual confirmation that my selections registered across multiple questions (Q4–Q6), forcing repeated clicks
- Inconsistent accessibility tree rendering on initial page load and question pages, making visual hierarchy assessment impossible
- Missing selection state feedback—no checkmark, highlight, or color change after clicking an option, violating recognition_over_recall principle

### home (10 mentions)
  Heuristics: help_documentation (4), visibility_of_system_status (3), accessibility_structure (2), recognition_over_recall (1)
- The missing accessibility tree violates the principle of **visibility_of_system_status**. A well-designed system should always communicate its state clearly. I can't see the page, so I can't verify whether the visual design supports the information architecture. The labeled nav links (Home, Framework, Assess, Chat, Heatmap) suggest multiple sections, but without seeing them rendered, I don't know if the hierarchy is clear or if there's cognitive overload.
- The navigation structure is clear and the primary action is unmissable. However, the initial blank/missing accessibility tree on first load is a real visibility_of_system_status problem—I had no indication the page was loading, failed, or slow. Now that elements are visible, the pattern is solid, but that initial state could lose impatient users.
- The accessibility tree being unavailable is a hard blocker for understanding page structure. I can't tell if there's explanatory copy, a hero statement, visual hierarchy, or context. The navigation is clear (good), but the page's *purpose* is invisible to me. This violates accessibility_structure — I can't orient myself to the page's information architecture or main message.

### results (9 mentions)
  Heuristics: accessibility_structure (5), visibility_of_system_status (4)
- The slide navigation (with 4 dots and prev/next buttons) suggests pagination, but I can't tell from the accessibility tree what content is on each slide. The 'Page 1 of 4' label is clear, but I have no way to know if I'm looking at a summary, detailed breakdown, comparison, or recommendations without scrolling/navigating. This creates cognitive friction for someone like me who wants to understand the *structure* before diving in.
- Critical issue: visibility_of_system_status. I can see buttons and navigation, but I cannot see my actual results data. No loading spinner, no error message, no 'your results are being processed' state. If the page is still loading, I have no indication. If it's an error, I don't know. The buttons are all clickable, which suggests the page *thinks* it's ready, but the content layer is opaque to me.
- Critical issue: The visibility of system status is unclear. I completed the assessment (evidenced by being on the results page), but I cannot see my actual results in the provided accessibility tree. The page has export buttons and navigation, but no visible content describing my assessment outcome, placement, or growth path. This violates the principle that users should always know what state the system is in. I should be able to immediately see my score/archetype/placement—that's the entire purpose of this page.

## Question Confusion Analysis

**option-item[value='1']** (32 confusion signals)
  Archetypes affected: student_non_designer, design_leader, career_changer, curious_explorer, agency_creative_director, ux_researcher
  - The page structure is straightforward. 'SAE Question 1 of 6' orients me immediately — I know where I am in the journey. The options are presented as a
  - I need to pick between Level 1 and Level 2. Level 1 says 'manually review and heavily rewrite everything' — that feels true to how I actually work. I 
  - I'm realizing I have a mental distinction between 'using AI as a thinking tool' (which I do, guilt-free) and 'AI-generated creative output' (which I d

**option-item[value='P']** (30 confusion signals)
  Archetypes affected: ai_native_engineer, student_non_designer, design_leader, curious_explorer, app_builder, agency_creative_director, traditional_craftsperson
  - I need to read all five options carefully before choosing. My persona reads every option because I care about precision. Looking at the stages: E is a
  - I'm noticing I'm overthinking this. My recent action history shows I've clicked options multiple times (0, I, I, A), which suggests either the interfa
  - I'm realizing I almost slipped into 'I' because it sounds more sophisticated. But I'm honest: I don't primarily think in terms of 'what does AI execut

**option-item[value='I']** (17 confusion signals)
  Archetypes affected: ai_native_engineer, traditional_craftsperson, daily_user, design_leader
  - I need to read each option carefully—that's how I work. Let me map these to my actual practice: E (Explorer) doesn't fit; my quality is consistent aft
  - I've clicked option 0 five times, which suggests either technical confusion (did my click not register?) or I was testing the interaction. That's not 
  - The question is asking about documentation practices across five maturity levels: E (Explorer, rarely documented), P (Practitioner, personal notes), I

**option-item[value='3']** (10 confusion signals)
  Archetypes affected: student_non_designer, app_builder
  - Six radio-button-style options arranged vertically, each representing an automation maturity level from 0-5. The progression is clear: manual → direct
  - Validating. The scale itself is well-designed — it maps real workflows I recognize, not arbitrary abstract levels. I'm not stuck between options or wo
  - Progress indicator shows 'Question 1 of 6' which helps orient me. The nav bar is consistent across pages. The option-items have aria-labels that inclu

**option-item[value='2']** (10 confusion signals)
  Archetypes affected: student_non_designer, daily_user, design_leader
  - The page structure is working well. I can see 'Question 2 of 6' (progress), the question itself, and six clearly labeled option items with aria-labels
  - The option labels are specific and self-explanatory—I don't need a tooltip to understand 'structured prompts with context, constraints, and output for
  - The question structure is clear ('Pick the automation level that best describes YOUR work') and the six options are logically sequenced from no automa

**option-item[value='4']** (7 confusion signals)
  Archetypes affected: ai_native_engineer, app_builder
  - Relief and mild validation. The question *gets* how I actually work — it's not asking 'Are you a prompt engineer?' or 'Do you use ChatGPT?' It's askin
  - Page structure is clear: I'm on Q3 of 6 (progress visible in context), options are labeled with aria-labels, Previous/Next buttons are available. No c
  - I almost second-guessed myself between Level 3 and 4. I *do* work in an IDE with LangGraph (that's Level 3), but I also maintain eval suites and run a

**option-item[value='A']** (6 confusion signals)
  Archetypes affected: traditional_craftsperson, app_builder
  - I'm looking at this through the lens of my 15 years in print/branding. Let me parse what each means: E is learning-only (not me); P is informal sharin
  - I notice I'm overthinking this — reading every word, weighing the subtle differences between I and A. That's very me: meticulous, careful. I'm not rus
  - The page structure is clear: five mutually exclusive options, each with a letter code and plain-language description. I can recognize which option fit

**option-item[value='E']** (6 confusion signals)
  Archetypes affected: career_changer, curious_explorer
  - The option descriptions are written in first-person ('I know when...', 'I can clearly explain...'), which makes them relatable and helps me match myse
  - I need to pick the option that honestly describes how I currently work. Looking at the options: E is 'write new prompts each time, nothing saved'—that
  - The option labels (E, P, I, A, S) are abstract letter codes that don't immediately tell me what they mean. I have to read the full description each ti

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| agency_creative_director | 5.0 | 5-5 | 0% |
| student_non_designer | 5.0 | 5-5 | 0% |
| traditional_craftsperson | 5.0 | 5-5 | 0% |
| ai_native_engineer | 6.0 | 6-6 | 0% |
| app_builder | 6.0 | 6-6 | 100% |
| career_changer | 6.0 | 6-6 | 0% |
| daily_user | 6.0 | 6-6 | 100% |
| design_leader | 6.0 | 6-6 | 0% |
| ux_researcher | 6.0 | 6-6 | 0% |
| curious_explorer | 7.0 | 7-7 | 100% |

## Flow Completion
- Completion rate: 100% (10/10)

## Self-Consistency Convergence
**Overall convergence rate:** None
**Archetypes analyzed:** 0


## Notable Self-Awareness Moments
- **traditional_craftsperson**: I'm noticing I'm applying print design standards to a web interface. I'm used to controlling every pixel in a static layout. Web means I can't control rendering, browser differences, user context. That's part of why I resist AI tools—they promise control and precision in a medium that's inherently variable. I should stay open to what this assessment actually does, even if the landing page delivery is imperfect.
- **traditional_craftsperson**: I'm someone who reads carefully and notices details. The pre-filled cohort value immediately caught my attention—not because it's wrong, but because I want to understand *why* it's there. As someone resistant to 'black box' design, I appreciate transparency in how systems handle my data. I'm also conscious that I might be overthinking an intake form, but that's who I am: meticulous.
- **traditional_craftsperson**: I notice I'm a bit relieved that the options are this explicit. I was worried—given the 'automation level' framing in the question—that this might be a tool designed primarily for engineers or developers, and that Level 0 would be treated as a non-answer or a gap to fill. But the design of these options shows the creator understands that some professionals legitimately don't use AI, and that's a valid data point. That's thoughtful. It makes me more willing to engage with whatever comes next.
- **traditional_craftsperson**: I'm noticing that my initial resistance to AI isn't just philosophical—it's also practical. I work in branding and print, where client relationships are built on personal expertise and hand-crafted solutions. If I were in a role where AI could genuinely accelerate routine work (like a content operations role), I might evaluate it differently. But for senior design work? The judgment call—the 'why this color, not that one'—that's where the value lives. I'm not dismissing AI as a tool; I'm being meticulous about where it belongs. That's very on-brand for me (conscientiousness: 5/5).
- **traditional_craftsperson**: I'm aware that my answer might mark me as a 'resistor' in this dataset. But I don't see that as a weakness — it's who I am. I'm also noticing I'm reading every option carefully (per my meticulous nature), even though the answer is clear to me. I'm not skimming. That's typical for me. And I'm cautious about clicking Next until I'm absolutely certain I've understood the question. I won't rush.
- **traditional_craftsperson**: I'm realizing this assessment is specifically about 'AI expertise' maturity stages, not design maturity. That's an important distinction I should have caught earlier. I initially misread 'automation level' as potentially referring to production automation (prepress, file workflows, asset management) — areas where I *do* embrace efficiency tools. But this is purely about generative AI prompting. My skepticism about AI isn't ignorance; it's informed choice based on my values around craft and human judgment. That said, I should acknowledge that the way levels 1–5 are phrased (increasingly technical/engineered) might not map cleanly to how most designers actually interact with AI. The gap between Level 1 and Level 2 seems large.
- **traditional_craftsperson**: I've clicked option[value='0'] four times in the recent actions log — that's odd. Either the UI didn't register my selection clearly, or I was second-guessing myself. Given my meticulous nature and skepticism about technology, I probably hesitated and clicked multiple times to confirm. That behavior reflects my discomfort with uncertain feedback from digital systems. I need to know the click registered, and apparently the interface didn't communicate that clearly enough.
- **traditional_craftsperson**: I'm realizing this entire assessment assumes a spectrum of AI adoption. The scale is literally calibrated for people *already using* AI — levels 1–5 are all about deepening AI workflow sophistication. Option 0 feels like the 'other' category for people like me who haven't adopted it. That's actually fine and honest, but it confirms my suspicion: this tool is designed for an audience that's already committed to AI. I'm not that audience.
- **traditional_craftsperson**: I've clicked option 0 five times, which suggests either technical confusion (did my click not register?) or I was testing the interaction. That's not typical for me — I usually read first, click once. This makes me wonder if there was a visibility issue with feedback. That said, looking at the options now, I'm confident in my judgment. My 15 years have taught me to trust my instinct when I've done the thinking work.
- **traditional_craftsperson**: I'm cautious about overstating my role. I'm a senior designer, but I'm not a design director or systems architect running org-wide standards. I do meticulous work and I do document it. I resist frameworks that feel imposed from above — I prefer to document *my* decisions for *my* craft. That's fundamentally the 'I' level. Also, I'm realizing this assessment is about work *maturity stages*, not skill level. I'm mature in my craft (15 years), but that doesn't mean I've graduated to creating systems for others.

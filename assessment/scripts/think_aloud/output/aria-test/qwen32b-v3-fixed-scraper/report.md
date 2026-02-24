# Think-Aloud Protocol Report

**Protocol:** v2.1 (10) | **Sessions:** 10 | **Avg NPS:** 5.4 | **NPS Std Dev:** 1.35 | **Pages/session:** 14.0

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
**Overall:** 49.0 (Grade D) | **Std Dev:** 18.2 | **Range:** 50.0 pts | **vs Benchmark (68):** below

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| career_changer | 25.0 | F | 25.0-25.0 |
| student_non_designer | 27.5 | F | 27.5-27.5 |
| traditional_craftsperson | 27.5 | F | 27.5-27.5 |
| ai_native_engineer | 40.0 | D | 40.0-40.0 |
| agency_creative_director | 55.0 | C | 55.0-55.0 |
| daily_user | 55.0 | C | 55.0-55.0 |
| ux_researcher | 55.0 | C | 55.0-55.0 |
| design_leader | 57.5 | C | 57.5-57.5 |
| app_builder | 72.5 | B | 72.5-72.5 |
| curious_explorer | 75.0 | B | 75.0-75.0 |

## Nielsen Heuristic Analysis
**Coverage:** 9/11 heuristics cited | **Citation rate:** 100%

| Heuristic | Count |
|-----------|-------|
| Recognition Over Recall | 58 |
| Visibility Of System Status | 27 |
| Match Real World | 18 |
| Help Documentation | 18 |
| User Control Freedom | 7 |
| Consistency Standards | 6 |
| Accessibility Structure | 3 |
| Flexibility Efficiency | 2 |
| Minimalist Design | 1 |

**Missing:** error_prevention, error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 370 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 46% |
| Notices Correct Action | 54% |
| Associates Action With Goal | 37% |
| Sees Progress | 76% |
| Understands Page Structure | 51% |

### assess?cohort=think-aloud-test (325 failures)
  Questions failed: will_try_right_effect, understands_page_structure, sees_progress, associates_action_with_goal, notices_correct_action
  Archetypes: daily_user, ux_researcher, design_leader, student_non_designer, career_changer, curious_explorer, app_builder, agency_creative_director, traditional_craftsperson, ai_native_engineer
  - [traditional_craftsperson] will_try_right_effect: I'm not entirely sure what clicking a button will do. The labels are vague for someone used to clear print-based design processes.
  - [traditional_craftsperson] notices_correct_action: There are buttons, but I don't see a clear call to action for starting the assessment or skipping demographics.
  - [traditional_craftsperson] associates_action_with_goal: The labels don't clearly communicate their purpose, like 'optional demographics' versus 'start'. I'm not confident in matching them to my goal.

### home (23 failures)
  Questions failed: will_try_right_effect, understands_page_structure, sees_progress, associates_action_with_goal, notices_correct_action
  Archetypes: daily_user, ux_researcher, design_leader, student_non_designer, career_changer, traditional_craftsperson, ai_native_engineer
  - [traditional_craftsperson] will_try_right_effect: I'm not confident that clicking 'Start' is the correct next step because the purpose of the page isn't immediately clear.
  - [traditional_craftsperson] notices_correct_action: The primary action is somewhat implied but lacks clear visual hierarchy or labeling to indicate that it's the correct next step.
  - [traditional_craftsperson] associates_action_with_goal: The label 'Start' is generic and doesn't directly communicate that it's the self-assessment I'm supposed to take.

### results (22 failures)
  Questions failed: will_try_right_effect, understands_page_structure, sees_progress, associates_action_with_goal, notices_correct_action
  Archetypes: daily_user, design_leader, student_non_designer, career_changer, ai_native_engineer
  - [daily_user] notices_correct_action: There’s no clear call to action like 'Continue' or 'Next Step,' so I’m unsure what to click next.
  - [daily_user] associates_action_with_goal: I don’t yet see how the labels or buttons map to my goal of understanding my results and next steps.
  - [daily_user] sees_progress: There’s no progress bar or confirmation that the results are final or that an action has been completed.

## Behavioral Realism
**Events/session:** 48.1 | **Total events:** 481

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| career_changer | 86 | 0.372 |
| traditional_craftsperson | 72 | 0.164 |
| student_non_designer | 70 | 0.36 |
| ux_researcher | 69 | 0.039 |
| design_leader | 67 | 0.086 |
| agency_creative_director | 39 | 0.098 |
| curious_explorer | 39 | 0.272 |
| daily_user | 30 | 0.109 |
| app_builder | 6 | 0.022 |
| ai_native_engineer | 3 | 0.056 |

## Accessibility Analysis (v2.1)
**Structure understanding rate:** 49% | **Accessibility rating:** 2.9/5 | **Accessibility thoughts:** 140

| Page | Structure Understanding |
|------|----------------------|
| assess?cohort=think-aloud-test | 47% |
| home | 70% |
| results | 56% |

| Archetype | Accessibility Rating |
|-----------|---------------------|
| career_changer | 2/5 |
| traditional_craftsperson | 2/5 |
| agency_creative_director | 3/5 |
| ai_native_engineer | 3/5 |
| app_builder | 3/5 |
| daily_user | 3/5 |
| design_leader | 3/5 |
| student_non_designer | 3/5 |
| ux_researcher | 3/5 |
| curious_explorer | 4/5 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (121 mentions)
  Heuristics: recognition_over_recall (54), visibility_of_system_status (21), help_documentation (17), match_real_world (14), user_control_freedom (7), consistency_standards (4), flexibility_efficiency (2), minimalist_design (1), accessibility_structure (1)
- The lack of clear differentiation between buttons violates the heuristic of 'consistency_standards', making it harder to identify the correct action.
- The options are clearly labeled, which helps in understanding what each level represents, but the visual presentation could be improved for better clarity.
- The question's framing does not match real-world design workflows for manual designers like myself.

### reflection (40 mentions)
- The interface didn't provide clear explanations or definitions for technical terms like 'harnesses' or 'agent infrastructure'.
- The visual hierarchy and layout were inconsistent, making it difficult to identify the selected option or the purpose of each question.
- There was no progress indicator, which made it hard to understand where I was in the overall journey.

### home (10 mentions)
  Heuristics: visibility_of_system_status (4), match_real_world (2), recognition_over_recall (2), help_documentation (1), accessibility_structure (1)
- The lack of a clear explanation about the purpose of 'DIT-MAED' on the landing page makes it harder to understand the context and relevance of the self-assessment.
- I can't tell how long the assessment will take or what it will ask — this could deter me from starting.
- The clear and prominent CTA aligns with the heuristic of recognition_over_recall, as the action is explicitly labeled and easy to understand.

### results (9 mentions)
  Heuristics: consistency_standards (2), visibility_of_system_status (2), recognition_over_recall (2), match_real_world (2), accessibility_structure (1)
- The lack of clear visual hierarchy between primary and secondary buttons could lead to confusion about which actions are most important.
- The lack of a clear section for results violates the heuristic of 'visibility_of_system_status' because I can't quickly locate my placement summary.
- The lack of clear labels on buttons makes it harder to understand their functions without trial and error.

## Question Confusion Analysis

**button.q-option[value='I']** (16 confusion signals)
  Archetypes affected: daily_user
  - The page lacks clear visual hierarchy for the maturity stages. The buttons are similar in style, making it hard to tell which one is selected or how t
  - I feel mildly anxious because I'm not sure if I'm interpreting the question correctly. The term 'maturity stage' isn't clearly explained, and I want t
  - The lack of progress indicators or section labels makes it hard to understand where I am in the process.

**#intakeStart** (9 confusion signals)
  Archetypes affected: traditional_craftsperson, curious_explorer, agency_creative_director
  - The 'Start Assessment' and 'Skip to questions' buttons are visually similar, making it unclear which one to click based on intent alone.
  - I'm not sure if I'm interpreting the buttons correctly, which makes me question my assumptions about the layout.
  - The lack of clear differentiation between buttons violates the heuristic of 'consistency_standards', making it harder to identify the correct action.

**button#epiasPrev** (5 confusion signals)
  Archetypes affected: traditional_craftsperson
  - The buttons for the maturity stages are labeled clearly but the visual hierarchy is confusing; I'm not sure which one I've already clicked on or if th
  - This interface assumes I'm familiar with AI maturity stages, but as a designer who rarely uses AI, I'm not sure how these labels apply to my workflow.
  - The buttons are labeled clearly, but the visual hierarchy isn't strong enough to guide my eye easily. I'm not sure which one I previously selected.

**button.q-option[value='2']** (5 confusion signals)
  Archetypes affected: daily_user
  - The options are laid out clearly with distinct labels, but the lack of visual feedback for selected options makes it unclear if a choice has been regi
  - This interface assumes a clear understanding of AI maturity levels, and I'm not sure if I'm interpreting Level 2 correctly — it feels like a middle-gr
  - The page is structured in a way that makes it easy to orient myself, but without labels for the progress or section, it’s hard to tell how many steps 

**button[aria-label="Level 2: I have reusable prompt templates with context and constraints sections."]** (5 confusion signals)
  Archetypes affected: student_non_designer, design_leader
  - The options are listed as buttons with labels, but the visual hierarchy is unclear. I don’t immediately see which button corresponds to the automation
  - The lack of clear visual feedback after clicking a button makes it hard to confirm my selection. I don’t see a highlight or any change in the UI to si
  - The layout is clean, but the buttons are labeled with letters (A, B, C, etc.) which don't align with the automation level descriptions. This could cau

**button[aria-label="Level 2: I run a checklist (consistency, quality standards, tone) before integrating AI output."]** (5 confusion signals)
  Archetypes affected: student_non_designer, ux_researcher
  - The page has buttons with labels that describe different levels of AI automation, but the formatting is inconsistent — some buttons are cut off or tru
  - I feel slightly confused because the design terminology is unfamiliar. I'm also a bit anxious about making the right choice since I can't go back to c
  - I'm realizing that my experience with AI tools in academia may not map cleanly to the automation levels described here. I'm not sure if I'm overestima

**button[aria-label="Level 2: I write structured prompts with context, constraints, and output format."]** (5 confusion signals)
  Archetypes affected: student_non_designer, ux_researcher
  - The page presents six options labeled A to F with brief descriptions. The buttons are styled similarly, but the labels use a terse format with line br
  - This interface assumes a level of familiarity with AI workflows that I may not fully have, especially in terms of design or production-level systems. 
  - The text on some buttons is cut off, which makes it hard to read the full option. This affects comprehension and decision-making.

**button[aria-label="Level 2: Usable outputs (screens, documents, code) from clear specs."]** (5 confusion signals)
  Archetypes affected: student_non_designer, ux_researcher
  - The layout is straightforward with each automation level clearly labeled and separated into buttons. However, the lack of visual feedback for previous
  - I realize that my understanding of automation levels might be incomplete, and I'm not sure if I'm overestimating or underestimating my use of AI tools
  - The interface uses clear labels for each option, making it easier to understand the differences between automation levels.

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| traditional_craftsperson | 3.0 | 3-3 | 0% |
| ai_native_engineer | 4.0 | 4-4 | 0% |
| career_changer | 4.0 | 4-4 | 0% |
| student_non_designer | 5.0 | 5-5 | 0% |
| agency_creative_director | 6.0 | 6-6 | 0% |
| app_builder | 6.0 | 6-6 | 0% |
| daily_user | 6.0 | 6-6 | 0% |
| design_leader | 6.0 | 6-6 | 0% |
| curious_explorer | 7.0 | 7-7 | 100% |
| ux_researcher | 7.0 | 7-7 | 100% |

## Flow Completion
- Completion rate: 90% (9/10)

## Self-Consistency Convergence
**Overall convergence rate:** None
**Archetypes analyzed:** 0


## Notable Self-Awareness Moments
- **traditional_craftsperson**: I’m not sure if this assessment is designed for someone with a background in branding and print design like mine. I’m used to a slower, more deliberate creative process, and I’m not sure if this tool aligns with that.
- **traditional_craftsperson**: I'm not sure if I'm interpreting the buttons correctly, which makes me question my assumptions about the layout.
- **traditional_craftsperson**: This interface assumes a working knowledge of AI tools, which I don't have. It makes me feel like an outsider in a space that's moving away from traditional design practices.
- **traditional_craftsperson**: This interface assumes that most professionals use AI tools regularly, which conflicts with my experience and values as a meticulous designer who prioritizes human judgment.
- **traditional_craftsperson**: I'm not familiar with terms like 'harnesses' or 'flagged exceptions' in the context of design. This makes me question if I'm interpreting the options correctly.
- **traditional_craftsperson**: This interface assumes some level of AI familiarity, which I don't have, but I'm glad it allows for my experience to be represented.
- **traditional_craftsperson**: This interface assumes some level of AI integration in design, which I don't have. I need to be careful to not over- or under-select based on how the options are phrased.
- **traditional_craftsperson**: I’m realizing that this interface assumes a working knowledge of AI tools, which I don’t have. It feels like it’s designed for someone with a different workflow than mine.
- **traditional_craftsperson**: This interface assumes a level of comfort with AI that I don’t have. It’s clear that the design is tailored for someone who uses AI regularly, which makes me question if the options will be relevant to my work process.
- **traditional_craftsperson**: This interface assumes I'm familiar with AI maturity stages, but as a designer who rarely uses AI, I'm not sure how these labels apply to my workflow.

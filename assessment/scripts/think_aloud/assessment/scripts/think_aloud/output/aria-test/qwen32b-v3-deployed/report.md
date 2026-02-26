# Think-Aloud Protocol Report

**Protocol:** v2.1 (10) | **Sessions:** 10 | **Avg NPS:** 5.5 | **NPS Std Dev:** 1.43 | **Pages/session:** 14.0

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
**Overall:** 50.8 (Grade D) | **Std Dev:** 15.6 | **Range:** 45.0 pts | **vs Benchmark (68):** below

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| career_changer | 30.0 | F | 30.0-30.0 |
| agency_creative_director | 35.0 | F | 35.0-35.0 |
| ai_native_engineer | 40.0 | D | 40.0-40.0 |
| traditional_craftsperson | 40.0 | D | 40.0-40.0 |
| student_non_designer | 45.0 | D | 45.0-45.0 |
| design_leader | 47.5 | D | 47.5-47.5 |
| curious_explorer | 62.5 | C | 62.5-62.5 |
| ux_researcher | 62.5 | C | 62.5-62.5 |
| daily_user | 70.0 | B | 70.0-70.0 |
| app_builder | 75.0 | B | 75.0-75.0 |

## Nielsen Heuristic Analysis
**Coverage:** 9/11 heuristics cited | **Citation rate:** 100%

| Heuristic | Count |
|-----------|-------|
| Recognition Over Recall | 66 |
| Visibility Of System Status | 32 |
| Help Documentation | 15 |
| Match Real World | 14 |
| Accessibility Structure | 3 |
| Consistency Standards | 2 |
| User Control Freedom | 2 |
| Minimalist Design | 1 |
| Flexibility Efficiency | 1 |

**Missing:** error_prevention, error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 374 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 44% |
| Notices Correct Action | 51% |
| Associates Action With Goal | 38% |
| Sees Progress | 79% |
| Understands Page Structure | 56% |

### assess?cohort=think-aloud-test (354 failures)
  Questions failed: will_try_right_effect, notices_correct_action, sees_progress, understands_page_structure, associates_action_with_goal
  Archetypes: app_builder, agency_creative_director, ux_researcher, traditional_craftsperson, design_leader, career_changer, curious_explorer, daily_user, student_non_designer, ai_native_engineer
  - [career_changer] sees_progress: After clicking, I'm not sure if the page will change or if something is loading. I might need a confirmation or progress indicator.
  - [career_changer] understands_page_structure: I'm not sure if the demographics section is optional or required. The labels don't clearly tell me what is important or how the page is structured.
  - [career_changer] will_try_right_effect: I'm not confident about what the right action is. I might read the question again or look for more guidance.

### home (14 failures)
  Questions failed: notices_correct_action, associates_action_with_goal, sees_progress, understands_page_structure, will_try_right_effect
  Archetypes: app_builder, ux_researcher, traditional_craftsperson, design_leader, career_changer, daily_user, curious_explorer, ai_native_engineer
  - [career_changer] sees_progress: The progress bar is there, but it doesn't change or update after clicking, so I'm not sure if it's working.
  - [career_changer] understands_page_structure: I can't clearly tell the main sections of the page because the labels or landmarks aren't obvious to me.
  - [design_leader] sees_progress: There is no visible progress indicator or feedback after clicking the 'Start' button.

### results (6 failures)
  Questions failed: will_try_right_effect, notices_correct_action, sees_progress, understands_page_structure, associates_action_with_goal
  Archetypes: ux_researcher, career_changer
  - [career_changer] will_try_right_effect: I'm not confident what the correct next step is. I might hover over buttons but hesitate to click anything without knowing what it does.
  - [career_changer] notices_correct_action: The buttons or options aren't clearly labeled in a way that tells me what they do. I'm not sure which one to pick.
  - [career_changer] associates_action_with_goal: The labels don't clearly connect to my goal of understanding what skills to learn next. I'm confused about how each option relates to that.

## Behavioral Realism
**Events/session:** 48.3 | **Total events:** 483

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| career_changer | 88 | 0.372 |
| traditional_craftsperson | 77 | 0.164 |
| design_leader | 67 | 0.086 |
| ux_researcher | 64 | 0.039 |
| student_non_designer | 55 | 0.36 |
| curious_explorer | 39 | 0.272 |
| agency_creative_director | 36 | 0.098 |
| daily_user | 36 | 0.109 |
| ai_native_engineer | 15 | 0.056 |
| app_builder | 6 | 0.022 |

## Accessibility Analysis (v2.1)
**Structure understanding rate:** 44% | **Accessibility rating:** 2.8/5 | **Accessibility thoughts:** 136

| Page | Structure Understanding |
|------|----------------------|
| assess?cohort=think-aloud-test | 40% |
| home | 90% |
| results | 67% |

| Archetype | Accessibility Rating |
|-----------|---------------------|
| ai_native_engineer | 2/5 |
| career_changer | 2/5 |
| ux_researcher | 2/5 |
| agency_creative_director | 3/5 |
| app_builder | 3/5 |
| curious_explorer | 3/5 |
| design_leader | 3/5 |
| student_non_designer | 3/5 |
| traditional_craftsperson | 3/5 |
| daily_user | 4/5 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (123 mentions)
  Heuristics: recognition_over_recall (60), visibility_of_system_status (28), help_documentation (15), match_real_world (13), user_control_freedom (2), accessibility_structure (2), consistency_standards (1), minimalist_design (1), flexibility_efficiency (1)
- The interface assumes I know whether to fill in optional information or not, but there's no clear guidance on what is required.
- The options are clearly labeled, which helps with understanding what each level entails. However, there's no visual hierarchy to guide me toward the most appropriate option for someone new to AI.
- The labels on the buttons are too abbreviated and jargon-heavy, making it hard to understand the options without prior knowledge.

### reflection (40 mentions)
- The interface assumes prior knowledge of AI jargon and workflows, which I don’t have as a UX Bootcamp student.
- There were no clear explanations or tooltips for the automation levels or maturity stages, making it hard to understand what each option meant.
- The lack of a progress indicator made it hard to track where I was in the assessment.

### home (10 mentions)
  Heuristics: recognition_over_recall (6), visibility_of_system_status (3), match_real_world (1)
- The 'Take the Assessment' button is clearly labeled, but there's no visual or textual guidance on what the assessment entails, which could help set expectations.
- The 'Take the Assessment' button is clearly labeled and matches the user's goal, which is a strength.
- The 'Take the Assessment' button is clearly labeled and stands out, which makes it easy to understand what the next action is.

### results (3 mentions)
  Heuristics: visibility_of_system_status (1), accessibility_structure (1), consistency_standards (1)
- The page lacks clear guidance on next steps, which is confusing for someone like me who is new to the field.
- The page is well-structured and the sections are clearly labeled, which helps me orient myself quickly.
- The clustering of similar actions (e.g., export options) could benefit from clearer visual separation to avoid accidental clicks.

## Question Confusion Analysis

**.q-option[aria-label='Level 0: I don't use AI tools — all my work is manual.']** (16 confusion signals)
  Archetypes affected: traditional_craftsperson
  - The options are labeled with letters, not numbers, which could confuse users expecting a 0-5 scale. This may lead to misinterpretation.
  - The page structure is clear with labeled options and navigation arrows. However, the lack of a visible progress indicator makes it hard to know where 
  - The options are labeled with letters (A-F) and short descriptions, but the labels are not clearly aligned with the buttons. The visual hierarchy is co

**button.q-option[aria-label='Level 1: Everything pauses — AI only works when I'm actively prompting.']** (12 confusion signals)
  Archetypes affected: agency_creative_director
  - I'm not sure if my process is being accurately captured. I use AI for brainstorming, but I don't want it to sound like I'm fully automating anything.
  - The descriptions are cut off, so I have to infer their full meaning. This could lead to confusion.
  - The buttons are labeled with letters (A-F) and incomplete text. It’s hard to read the full options, especially for B, C, and D, which get cut off. Thi

**button[aria-label='Level 4: End-to-end features that are generated, tested, and QA'd automatically.']** (10 confusion signals)
  Archetypes affected: ai_native_engineer
  - The page layout is clean, but the options are not clearly separated, making it hard to focus on one at a time.
  - The lack of a clear explanation of what 'maturity stage' means could confuse users who are not familiar with the term.
  - The page structure is somewhat clear, but there's no progress indicator, making it hard to gauge where I am in the assessment.

**#intakeSkip** (9 confusion signals)
  Archetypes affected: traditional_craftsperson, curious_explorer, career_changer, ux_researcher
  - I will click 'Skip to start' because I'm not sure if the demographics form is required and I just want to get to the assessment.
  - I'm not sure if I should have filled in the demographics form, but I don't want to spend time on something optional if I'm not sure it matters.
  - The page structure is clear enough to identify the 'Skip to start' button, but without more context, I'm not sure if I'm making the right choice.

**button[aria-label='Level 1: I manually review and heavily rewrite everything AI produces.']** (7 confusion signals)
  Archetypes affected: curious_explorer
  - The buttons for each automation level are clearly labeled and spaced out, but the text is cut off slightly for some options, making it hard to read th
  - I'm not sure if I'm using AI as much as others in my field, but I'm definitely trying to learn more and integrate it into my workflow.
  - The options are labeled with letters (A, B, C, etc.), but the descriptions are cut off and hard to read fully. It's unclear which option is the correc

**#intakeStart** (6 confusion signals)
  Archetypes affected: design_leader, daily_user
  - The page is clean, but the main call-to-action is not immediately prominent. The 'Start Assessment' and 'Skip to questions' buttons are both visually 
  - I’m assuming this tool is designed for a broad audience, but I’m not sure how much it caters to those who are less familiar with AI. I want to make su
  - The two similar buttons for starting the assessment could lead to confusion about which one to click. This is a usability concern under 'consistency_s

**button[aria-label='Level 1: I use ChatGPT or Midjourney for ideas and drafts, but I direct every step.']** (6 confusion signals)
  Archetypes affected: curious_explorer
  - The buttons for each automation level are clearly labeled, but the visual hierarchy is a bit confusing since all buttons look the same size and color.
  - I feel excited to see how my experience fits into this framework, but also slightly anxious because I'm not sure if I'm choosing the 'right' level.
  - I'm not sure how much of my work is actually automated — I'm still learning what tools are available.

**button.q-option[aria-label='Level 2: I write structured prompts with context, constraints, and output format.']** (5 confusion signals)
  Archetypes affected: daily_user, agency_creative_director
  - The buttons are labeled with letters (A-F) and abbreviated text, making it hard to quickly understand what each maturity level represents. I need more
  - The page lacks a clear progress indicator or orientation cues, making it hard to understand where I am in the journey. This could increase anxiety and
  - The buttons for each automation level are clearly labeled, but the lack of visual hierarchy makes it hard to quickly identify the most relevant option

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| career_changer | 3.0 | 3-3 | 0% |
| ai_native_engineer | 4.0 | 4-4 | 0% |
| traditional_craftsperson | 4.0 | 4-4 | 0% |
| agency_creative_director | 5.0 | 5-5 | 0% |
| design_leader | 6.0 | 6-6 | 0% |
| student_non_designer | 6.0 | 6-6 | 0% |
| ux_researcher | 6.0 | 6-6 | 0% |
| app_builder | 7.0 | 7-7 | 100% |
| curious_explorer | 7.0 | 7-7 | 100% |
| daily_user | 7.0 | 7-7 | 100% |

## Flow Completion
- Completion rate: 30% (3/10)

## Self-Consistency Convergence
**Overall convergence rate:** None
**Archetypes analyzed:** 0


## Notable Self-Awareness Moments
- **career_changer**: I feel like I'm behind in tech and not as advanced as others. This interface assumes I know what to do, but I'm still learning.
- **career_changer**: I'm not sure if I should have filled in the demographics form, but I don't want to spend time on something optional if I'm not sure it matters.
- **career_changer**: I'm not as advanced as I thought. The options assume I'm already using AI tools, but I'm still learning and haven't integrated them into my workflow yet.
- **career_changer**: I'm not as confident as I need to be in tech. This question assumes some familiarity with AI workflows, which I don't have yet.
- **career_changer**: I realize I'm not as advanced as I need to be in AI, and this question assumes some level of familiarity that I don’t fully have yet.
- **career_changer**: I’m not as advanced as I hoped in using AI. I’m still learning the basics, and the language used here (like 'context blocks' or 'harness configs') makes me feel like I don't belong here.
- **career_changer**: I'm not as advanced in tech as the options assume. This feels like it's tailored for people with more hands-on AI experience than I have.
- **career_changer**: I'm not as advanced as I thought. I don't even know what 'agent infrastructure' or 'self-improving harnesses' mean, and I'm already feeling behind.
- **career_changer**: I'm not as advanced as I thought. The options imply a level of AI integration I haven't reached yet.
- **career_changer**: I'm realizing that I might not be as familiar with AI maturity stages as I thought. This makes me feel even more behind in the job market.

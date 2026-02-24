# Think-Aloud Protocol Report

**Protocol:** v2.0 (60) | **Sessions:** 60 | **Avg NPS:** 6.4 | **NPS Std Dev:** 1.07 | **Pages/session:** 14.0

## Persona Coverage
- agency_creative_director: 6 sessions
- ai_native_engineer: 6 sessions
- app_builder: 7 sessions
- career_changer: 5 sessions
- curious_explorer: 6 sessions
- daily_user: 5 sessions
- design_leader: 6 sessions
- student_non_designer: 6 sessions
- traditional_craftsperson: 7 sessions
- ux_researcher: 6 sessions

## SUS Scores (System Usability Scale)
**Overall:** 58.5 (Grade C) | **Std Dev:** 13.8 | **Range:** 57.5 pts | **vs Benchmark (68):** below

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| career_changer | 34.0 | F | 25.0-42.5 |
| traditional_craftsperson | 47.9 | D | 35.0-67.5 |
| agency_creative_director | 49.5 | C | 37.5-60.0 |
| student_non_designer | 52.9 | D | 42.5-67.5 |
| ux_researcher | 53.3 | D | 42.5-67.5 |
| design_leader | 64.2 | C | 60.0-67.5 |
| daily_user | 67.0 | C | 57.5-70.0 |
| ai_native_engineer | 67.5 | B | 65.0-70.0 |
| app_builder | 68.9 | C | 67.5-70.0 |
| curious_explorer | 75.8 | B | 70.0-82.5 |

## Nielsen Heuristic Analysis
**Coverage:** 10/10 heuristics cited | **Citation rate:** 100%

| Heuristic | Count |
|-----------|-------|
| Match Real World | 268 |
| Recognition Over Recall | 245 |
| Visibility Of System Status | 150 |
| User Control Freedom | 42 |
| Help Documentation | 40 |
| Consistency Standards | 32 |
| Minimalist Design | 25 |
| Error Prevention | 23 |
| Flexibility Efficiency | 7 |
| Error Recovery | 7 |

## Cognitive Walkthrough Failure Points
**Total failures:** 1849 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 53% |
| Notices Correct Action | 61% |
| Associates Action With Goal | 66% |
| Sees Progress | 40% |

### assess?cohort=think-aloud-test (1457 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, sees_progress, will_try_right_effect
  Archetypes: traditional_craftsperson, student_non_designer, ai_native_engineer, curious_explorer, daily_user, ux_researcher, design_leader, agency_creative_director, career_changer, app_builder
  - [app_builder] will_try_right_effect: Can't see the actual page content due to accessibility tree being unavailable - no clear understanding of what actions are available
  - [app_builder] notices_correct_action: Without visual access to the interface, can't identify specific buttons or form elements to interact with
  - [app_builder] associates_action_with_goal: Can't evaluate action labels or visual cues since the page content isn't visible

### results (201 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, sees_progress, will_try_right_effect
  Archetypes: traditional_craftsperson, student_non_designer, ai_native_engineer, curious_explorer, daily_user, ux_researcher, design_leader, agency_creative_director, career_changer, app_builder
  - [app_builder] will_try_right_effect: No content is visible, so I have no idea what my goal should be or what actions are available
  - [app_builder] notices_correct_action: Can't identify any interactive elements or navigation options without the accessibility tree
  - [app_builder] associates_action_with_goal: Without seeing any UI elements, there's no way to connect actions to intended outcomes

### home (191 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, sees_progress, will_try_right_effect
  Archetypes: traditional_craftsperson, student_non_designer, ai_native_engineer, curious_explorer, daily_user, ux_researcher, design_leader, agency_creative_director, career_changer, app_builder
  - [app_builder] will_try_right_effect: Can't see the page content due to accessibility tree being unavailable - this is a UX friction point that would make me bounce
  - [app_builder] notices_correct_action: No visible interface elements to interact with, can't locate the assessment entry point
  - [app_builder] associates_action_with_goal: Without seeing any CTAs or navigation, I can't map actions to my goal of taking the self-assessment

## Behavioral Realism
**Events/session:** 41.3 | **Total events:** 2479

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| career_changer | 77 | 0.413 |
| student_non_designer | 67 | 0.323 |
| design_leader | 53.7 | 0.051 |
| ux_researcher | 52.8 | 0.12 |
| traditional_craftsperson | 41.1 | 0.164 |
| curious_explorer | 37.7 | 0.259 |
| agency_creative_director | 26.8 | 0.097 |
| ai_native_engineer | 26 | 0.077 |
| daily_user | 21.6 | 0.147 |
| app_builder | 16.3 | 0.016 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (723 mentions)
  Heuristics: match_real_world (266), recognition_over_recall (240), visibility_of_system_status (68), user_control_freedom (39), help_documentation (35), consistency_standards (30), error_prevention (22), minimalist_design (12), error_recovery (7), flexibility_efficiency (4)
- Good that they pre-filled the cohort parameter from the URL and made demographics optional with a clear skip option. Reduces friction while still collecting useful data.
- Good use of concrete examples rather than abstract descriptions - makes it easy to self-identify without ambiguity about what each level means in practice.
- Good progressive disclosure - each option builds on the previous with clear technical distinctions. No ambiguity about what each level means in practice.

### reflection (224 mentions)
- Accessibility tree frequently unavailable, making interface evaluation impossible
- No visual feedback on selected options - couldn't tell if clicks registered
- Results page didn't prominently display actual assessment outcomes

### home (60 mentions)
  Heuristics: visibility_of_system_status (33), minimalist_design (8), recognition_over_recall (5), help_documentation (4), flexibility_efficiency (3), user_control_freedom (3), match_real_world (2), error_prevention (1), consistency_standards (1)
- The landing page doesn't give me enough system context - what am I assessing, how long will it take, what's the output?
- The 'Take the Assessment' button is prominently displayed and clearly labeled, which helps direct me to my primary goal without confusion.
- The accessibility tree being unavailable suggests potential accessibility issues or technical problems that could exclude users with disabilities - this is a critical concern in fintech where regulatory compliance matters.

### results (56 mentions)
  Heuristics: visibility_of_system_status (49), minimalist_design (5), help_documentation (1), consistency_standards (1)
- The results page doesn't show me my actual results prominently - I have to infer from action buttons what my next steps might be. This violates basic feedback principles.
- The system isn't clearly showing me the most important information - my actual results. I can see action buttons but not the core content I came here for.
- The system isn't clearly communicating my status or results - I can see action buttons but no visual feedback about where I placed or what my results mean.

## Question Confusion Analysis

**[value='P']** (35 confusion signals)
  Archetypes affected: traditional_craftsperson, agency_creative_director, ai_native_engineer, curious_explorer, ux_researcher, design_leader, career_changer, app_builder
  - Pleasantly surprised - this question actually captures the operational reality of production AI systems. The distinction between having escalation pat
  - I realize I'm somewhere between the cowboy 'trust my judgment' approach and formal enterprise governance. At a startup, you need enough process to not
  - Looking at these options, I realize I'm probably somewhere between 'hit-or-miss' and 'predictable.' I'm not advanced enough to have full task workflow

**[value='1']** (29 confusion signals)
  Archetypes affected: student_non_designer, agency_creative_director, curious_explorer, ux_researcher, design_leader, career_changer
  - The question framing 'when laptop is closed' is confusing for UX research work. As a researcher, most of my AI-assisted work happens during active ana
  - The options don't map well to research workflows - they assume output types that don't exist in UX research. This is a fundamental mismatch between th
  - The progression from manual to automated is logical and the language clearly distinguishes between different levels of human oversight versus system a

**[value='4']** (26 confusion signals)
  Archetypes affected: ai_native_engineer, app_builder
  - I need to pick between level 3 (IDE with multi-step workflows) and level 4 (automated agent harnesses with eval suites). Level 3 mentions context engi
  - I'm somewhere between level 3 and 4. I do work in IDEs with multi-step workflows and context engineering, but I also build autonomous agent systems wi
  - I need to pick between options 3, 4, and 5. Option 4 'Automated eval suites decide pass, retry, or escalate without my input' best matches my LangGrap

**[value='3']** (21 confusion signals)
  Archetypes affected: ux_researcher, ai_native_engineer, app_builder, student_non_designer
  - Actually impressed - this question captures the nuance between basic AI assistance and full automation. Option 3 perfectly describes modern agent orch
  - I was wrong to dismiss this as overly simplistic. The distinction between options 2, 3, and 4 actually maps well to the reality of current AI developm
  - I can see this is about QA/automation levels in AI work. The options range from manual review to self-correcting systems. The progression looks more s

**option-item[value='3']** (20 confusion signals)
  Archetypes affected: app_builder, student_non_designer, ai_native_engineer
  - Actually impressed - this question gets at real implementation details rather than surface-level AI usage. Shows they understand the difference betwee
  - I'm somewhere between options 2 and 3. I don't run full checklists every time, but I do have review gates for production code. Option 3 better reflect
  - I'm realizing I'm probably between levels 3 and 4. I use AI heavily in my IDE and ship AI-generated components daily, but I don't have fully autonomou

**option-item[value='P']** (19 confusion signals)
  Archetypes affected: daily_user, app_builder, student_non_designer, ai_native_engineer
  - Looking at these options, I need to honestly assess where I am. I build with Cursor/Claude daily and ship components, but this is specifically about r
  - This question is about ownership/decision boundaries between human and AI. The options range from 'Blurry' (E) to organizational norm-setting (S). The
  - The question framing was initially confusing because 'maturity stage' sounded like business jargon, but the actual options are technically precise and

**option-item[value='1']** (15 confusion signals)
  Archetypes affected: daily_user, career_changer, student_non_designer
  - The options are clearly laid out in progressive order from no AI to full automation, making it easy to understand the spectrum, but seeing all the adv
  - The question assumes I have professional work experience, but as a bootcamp student transitioning careers, I don't have established UX work patterns y
  - I need to be honest about where I actually am, even though it feels vulnerable. I'm probably between 'None' and 'Ideas, copy drafts, and visual concep

**[value='I']** (13 confusion signals)
  Archetypes affected: ux_researcher, ai_native_engineer, app_builder
  - Good that we're on the final question and the progression feels logical. However, still frustrated by the inaccessible accessibility tree making it ha
  - This question actually feels more relevant than the previous ones - it's getting at real operational maturity rather than just technical knowledge. I 
  - I realize there's a difference between my technical sophistication with AI and my organizational reach. I might be an expert user but not necessarily 

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| student_non_designer | 5.3 | 4-7 | 67% |
| traditional_craftsperson | 5.3 | 4-6 | 57% |
| ux_researcher | 5.7 | 4-6 | 100% |
| agency_creative_director | 6.0 | 4-7 | 80% |
| design_leader | 6.2 | 5-8 | 100% |
| career_changer | 6.8 | 6-7 | 100% |
| ai_native_engineer | 7.0 | 7-7 | 100% |
| daily_user | 7.0 | 7-7 | 100% |
| app_builder | 7.1 | 7-8 | 100% |
| curious_explorer | 7.5 | 7-8 | 100% |

## Flow Completion
- Completion rate: 98% (59/60)

## Self-Consistency Convergence
**Overall convergence rate:** 0.02
**Archetypes analyzed:** 10

- **app_builder**: 1 robust / 96 total (1% convergence)
- **career_changer**: 2 robust / 68 total (3% convergence)
- **ux_researcher**: 0 robust / 84 total (0% convergence)
- **student_non_designer**: 4 robust / 80 total (5% convergence)
- **ai_native_engineer**: 1 robust / 83 total (1% convergence)
- **agency_creative_director**: 1 robust / 82 total (1% convergence)
- **design_leader**: 0 robust / 84 total (0% convergence)
- **curious_explorer**: 3 robust / 80 total (4% convergence)
- **traditional_craftsperson**: 1 robust / 97 total (1% convergence)
- **daily_user**: 1 robust / 69 total (1% convergence)

## Notable Self-Awareness Moments
- **app_builder**: My impatience with unclear interfaces is showing - I'm already wanting to peek at the Framework section to understand what this assesses, but I'll stick to the direct path for now.
- **app_builder**: I'm wondering if 'Creative Technologist' will be understood by their system, or if I should use something more standard like 'Full Stack Developer' - but I'll stick with my actual title.
- **app_builder**: Looking at these options, I'm definitely in the 'fluent' category but not at the full automation end. I'm hands-on with multi-step workflows but not running fully autonomous agent harnesses yet.
- **app_builder**: I'm somewhere between options 2 and 3. I don't run full checklists every time, but I do have review gates for production code. Option 3 better reflects having systematic but lightweight processes.
- **app_builder**: I'm realizing I'm probably between levels 3 and 4. I use AI heavily in my IDE and ship AI-generated components daily, but I don't have fully autonomous systems running yet. Most of my AI work requires my presence and oversight.
- **app_builder**: I'm solidly in the 'engineer context blocks' camp. I build system prompts with examples and rules for my components, but I haven't built full harness systems with retry logic yet. That's probably the next level up.
- **app_builder**: This is making me realize I'm probably not as automated as I sometimes think. I use AI heavily but I'm still the one designing the workflows, doing the integration work, and catching the edge cases. Level 3 seems right - large features through orchestrated workflows with my QA checkpoints.
- **app_builder**: This question actually captures my work well - I'm definitely in that sweet spot of maintaining shared workflows and context libraries rather than just ad-hoc prompting or full production infrastructure.
- **app_builder**: Honestly, while I'm fluent with AI tools, my multi-step workflows do sometimes break. I'm probably at the 'reliable with checkpoints' stage - I have a process but it's not yet foolproof with clear intervention points.
- **app_builder**: I'm realizing this assessment is getting pretty specific about AI workflow maturity. I'm probably in that intermediate zone - beyond basics but not yet at the architect level where I'm building reusable systems.

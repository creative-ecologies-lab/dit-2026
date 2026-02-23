# Think-Aloud Protocol Report

**Protocol:** v2.0 (7) | **Sessions:** 7 | **Avg NPS:** 7.1 | **NPS Std Dev:** 0.69 | **Pages/session:** 14.0

## Persona Coverage
- agency_creative_director: 1 sessions
- ai_native_engineer: 1 sessions
- app_builder: 1 sessions
- curious_explorer: 1 sessions
- design_leader: 1 sessions
- student_non_designer: 1 sessions
- traditional_craftsperson: 1 sessions

## SUS Scores (System Usability Scale)
**Overall:** 63.9 (Grade C) | **Std Dev:** 12.6 | **Range:** 40.0 pts | **vs Benchmark (68):** below

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| agency_creative_director | 37.5 | D | 37.5-37.5 |
| student_non_designer | 62.5 | C | 62.5-62.5 |
| ai_native_engineer | 65.0 | C | 65.0-65.0 |
| design_leader | 67.5 | C | 67.5-67.5 |
| traditional_craftsperson | 67.5 | C | 67.5-67.5 |
| app_builder | 70.0 | B | 70.0-70.0 |
| curious_explorer | 77.5 | B | 77.5-77.5 |

## Nielsen Heuristic Analysis
**Coverage:** 9/10 heuristics cited | **Citation rate:** 100%

| Heuristic | Count |
|-----------|-------|
| Recognition Over Recall | 34 |
| Match Real World | 27 |
| Error Prevention | 12 |
| Minimalist Design | 7 |
| Help Documentation | 5 |
| Visibility Of System Status | 5 |
| User Control Freedom | 4 |
| Consistency Standards | 3 |
| Flexibility Efficiency | 1 |

**Missing:** error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 32 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 3% |
| Notices Correct Action | 3% |
| Associates Action With Goal | 24% |
| Sees Progress | 2% |

### assess?cohort=think-aloud-test (24 failures)
  Questions failed: associates_action_with_goal, sees_progress, will_try_right_effect
  Archetypes: design_leader, ai_native_engineer, traditional_craftsperson, curious_explorer, agency_creative_director, student_non_designer
  - [design_leader] associates_action_with_goal: Level 3-5 descriptions use technical jargon (IDE, eval suites, agent harnesses) that would confuse many of my designers
  - [design_leader] will_try_right_effect: These automation levels don't map to design work - we don't have 'harnesses' or 'IDE workflows'
  - [design_leader] associates_action_with_goal: None of these levels describe how designers actually work with AI tools - this feels like a dev assessment

### results (7 failures)
  Questions failed: associates_action_with_goal, notices_correct_action, will_try_right_effect
  Archetypes: agency_creative_director, app_builder, ai_native_engineer
  - [agency_creative_director] will_try_right_effect: This feels more like a report card than actionable guidance - where do I actually go from here?
  - [agency_creative_director] notices_correct_action: I see suggested next steps in text but no clear buttons or links to actually take those steps
  - [agency_creative_director] associates_action_with_goal: The growth path advice is vague - 'turn prompts into reusable patterns' doesn't tell me HOW

### home (1 failures)
  Questions failed: associates_action_with_goal
  Archetypes: student_non_designer
  - [student_non_designer] associates_action_with_goal: I don't know what 'SAE automation level' or 'E-P-I-A-S maturity stage' actually mean in practical terms - the acronyms are opaque

## Behavioral Realism
**Events/session:** 41.6 | **Total events:** 291

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| student_non_designer | 67 | 0.354 |
| design_leader | 55 | 0.056 |
| traditional_craftsperson | 43 | 0.156 |
| ai_native_engineer | 36 | 0.04 |
| curious_explorer | 34 | 0.31 |
| agency_creative_director | 32 | 0.094 |
| app_builder | 24 | 0.061 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (84 mentions)
  Heuristics: recognition_over_recall (29), match_real_world (27), error_prevention (12), user_control_freedom (4), help_documentation (4), visibility_of_system_status (3), consistency_standards (2), minimalist_design (2), flexibility_efficiency (1)
- The form maintains state well across navigation, and the clear labeling of optional fields reduces pressure while still encouraging participation.
- Good that the Next button is disabled until I make a selection - prevents accidental progression. The levels are clearly numbered and build logically.
- Good progression from manual to automated, with concrete examples that help me place myself accurately.

### reflection (23 mentions)
- Some questions used developer-focused language (IDE workflows, harnesses) that doesn't translate well to design contexts
- The laptop automation question felt completely irrelevant to design workflows
- Acronyms like E-P-I-A-S and SAE weren't immediately defined on the landing page

### home (7 mentions)
  Heuristics: recognition_over_recall (5), visibility_of_system_status (2)
- The page uses acronyms (E-P-I-A-S, SAE) without immediate definition, which could be confusing for users unfamiliar with the framework. The 'Review the framework' link helps, but key terms should be more accessible upfront.
- The page gives clear expectations about what the assessment includes (question counts, output types) which helps me understand the commitment before starting.
- Good that they clearly state what the assessment includes upfront — 11 questions broken down into 6 + 5, with specific outcomes promised. This transparency helps me decide if it's worth my time.

### results (7 mentions)
  Heuristics: minimalist_design (5), help_documentation (1), consistency_standards (1)
- The framework excerpts provide good context but feel overwhelming at the bottom. The key insight about depth beating breadth could be highlighted better since it's the core philosophy that changes how leaders think about AI adoption.
- The framework excerpts provide good context for understanding the assessment logic, but they're quite text-heavy. The concrete next steps are helpful but I need more specificity about what 'eval checks' means in a design context.
- The framework excerpts at the bottom provide good context but they're quite lengthy. I appreciate the detail as someone who reads carefully, but the wall of text could be overwhelming for others.

## Question Confusion Analysis

**input[name='epias_l1_judgment'][value='E']** (5 confusion signals)
  Archetypes affected: agency_creative_director, curious_explorer
  - Hmm, this is making me think about my actual AI knowledge. I'm definitely enthusiastic and use AI tools, but honestly I'm still learning what works we
  - I think I'm somewhere between Explorer and Practitioner. I have some sense of when AI might help, but I'm definitely still figuring out the boundaries
  - The question feels more personal and introspective than the previous ones. 'How well do you know when AI helps versus hurts?' cuts right to the heart 

**input[name='epias_l3_ownership'][value='P']** (4 confusion signals)
  Archetypes affected: app_builder, student_non_designer
  - This is the final question of the assessment, asking about 'division of work between human and AI'. The options progress from individual confusion to 
  - I need to think about my actual research workflow with AI models. When I'm training models or using tools like GitHub Copilot, do I have clear boundar
  - The progression from personal confusion to organizational leadership is clear and logical. Each option builds naturally on the previous one in terms o

**input[name='sae_reuse'][value='1']** (3 confusion signals)
  Archetypes affected: agency_creative_director, design_leader
  - Final question about workflow reusability - this is the most enterprise-relevant question so far. The progression from 'save prompts' to 'production-g
  - Looking at my actual usage, I'm somewhere between level 1 and 2. I save prompts for design reviews and user research, sometimes with basic templates, 
  - The progression from Level 1 to Level 5 feels like it jumps skill categories entirely - from basic user behaviors to technical infrastructure manageme

**input[name='sae_qa'][value='3']** (3 confusion signals)
  Archetypes affected: app_builder, student_non_designer, ai_native_engineer
  - I need to map my actual QA process to these options. I do use evaluation metrics and have structured review processes in my research workflows, but th
  - I'm genuinely between Level 3 and 4. I do have explicit evals and review gates, but not quite full automation deciding pass/retry/escalate without my 
  - The radio options progress from manual to fully automated QA, which maps well to actual development maturity levels. The wording is specific enough to

**input[name='epias_l1_accountability'][value='P']** (3 confusion signals)
  Archetypes affected: agency_creative_director, curious_explorer
  - Hmm, accountability... I'm realizing I probably fall somewhere between Explorer and Practitioner. I do try to check AI output, but I'm not super syste
  - I'm realizing I'm somewhere between Practitioner and Integrator. I do manually verify everything - my design eye won't let me just accept AI output. B
  - The options create a clear maturity progression, but I'm noticing the gap between Practitioner (manual verification) and Integrator (documentation) fe

**input[name='sae_prompting'][value='4']** (3 confusion signals)
  Archetypes affected: app_builder, ai_native_engineer
  - I'm between Level 4 and 5. I do build harness configs with evals and retry logic in my LangGraph workflows, but Level 5's description feels incomplete
  - Clean progression from basic prompting to full automation. The levels are well-defined and I can see clear technical distinctions between each tier.
  - This question hits the sweet spot - it's asking about actual implementation patterns I work with. Finally something that distinguishes between people 

**input[name='sae_reuse'][value='4']** (3 confusion signals)
  Archetypes affected: app_builder, ai_native_engineer
  - I need to pick between Level 4 and 5 here. I build production-grade agent infrastructure with LangGraph that others in my startup use, but I wouldn't 
  - I'm realizing there's a gap between my day-to-day AI tooling fluency and building truly autonomous systems. I ship AI components but haven't built the
  - Good that this is the final question and the levels feel measurable rather than subjective. The distinction between 4 and 5 is clear - operational vs 

**input[name='sae_tools'][value='1']** (2 confusion signals)
  Archetypes affected: design_leader, curious_explorer
  - The progression from Level 0 to Level 5 is clear, but the jump from Level 1 (ChatGPT/Midjourney) to Level 2 (app-builders) to Level 3 (IDE workflows) 
  - I'm definitely somewhere between Level 1 and Level 2. I use ChatGPT for brainstorming and ideation, and I've dabbled with Midjourney for mood boards, 

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| traditional_craftsperson | 6.0 | 6-6 | 100% |
| agency_creative_director | 7.0 | 7-7 | 100% |
| ai_native_engineer | 7.0 | 7-7 | 100% |
| app_builder | 7.0 | 7-7 | 100% |
| student_non_designer | 7.0 | 7-7 | 100% |
| curious_explorer | 8.0 | 8-8 | 100% |
| design_leader | 8.0 | 8-8 | 100% |

## Flow Completion
- Completion rate: 100% (7/7)

## Self-Consistency Convergence
**Overall convergence rate:** None
**Archetypes analyzed:** 0


## Notable Self-Awareness Moments
- **design_leader**: My instinct to review the framework first rather than jumping into the assessment reflects my methodical nature. I realize I'm evaluating this through my 'weakest team member' lens - will a junior designer understand what E-P-I-A-S and SAE mean?
- **design_leader**: I'm being characteristically careful here - filling out optional fields because I know data quality matters for getting meaningful results. This is the same thoroughness I bring to vendor evaluations.
- **design_leader**: This is forcing me to separate my role as someone who needs to understand AI strategy from my personal hands-on usage. Personally, I'm still quite traditional in my design process.
- **design_leader**: I'm realizing I'm somewhere in the middle here. I do use AI occasionally, but I'm not as systematic about QA as I probably should be. I definitely manually review everything, but I don't have formal checklists yet.
- **design_leader**: I'm realizing this assessment might be built for developers, not designers. The laptop question assumes I have automated workflows running, but in design work, most collaboration and iteration happens manually.
- **design_leader**: I'm realizing this question exposes a gap in my knowledge. As a design leader, I use AI occasionally but I'm not deeply technical about prompting. I write basic prompts and adjust them until they work, but I don't know what 'harness configs' or 'eval gates' even are.
- **design_leader**: Looking at these levels makes me realize how much room there is for growth in AI-assisted design production. My team and I are still quite early in this journey, focusing more on ideation than actual artifact generation.
- **design_leader**: I'm realizing I've been thinking more about AI strategy than actually building reusable workflows. My 'moderate' AI usage means I'm still in the experimentation phase, not the systematization phase. That's probably normal for leadership roles.
- **design_leader**: I'm realizing there's a gap between my leadership aspirations around AI and my actual personal practice. I want to be the Steward setting standards, but honestly I'm probably more at the Practitioner level with some saved approaches that work.
- **design_leader**: I realize I'm probably more advanced than 'Practitioner' since I've been thinking systematically about team adoption, but I'm not quite at the 'Steward' level of setting organizational policy. That's above my pay grade - I influence but don't set company-wide AI policy.

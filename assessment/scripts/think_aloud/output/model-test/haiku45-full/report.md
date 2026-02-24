# Think-Aloud Protocol Report

**Protocol:** v2.0 (50) | **Sessions:** 50 | **Avg NPS:** 5.7 | **NPS Std Dev:** 2.83 | **Pages/session:** 8.7

## Persona Coverage
- agency_creative_director: 5 sessions
- ai_native_engineer: 5 sessions
- app_builder: 5 sessions
- career_changer: 5 sessions
- curious_explorer: 5 sessions
- daily_user: 5 sessions
- design_leader: 5 sessions
- student_non_designer: 5 sessions
- traditional_craftsperson: 5 sessions
- ux_researcher: 5 sessions

## SUS Scores (System Usability Scale)
**Overall:** 70.6 (Grade B) | **Std Dev:** 16.3 | **Range:** 57.5 pts | **vs Benchmark (68):** above

| Archetype | Mean SUS | Grade | Range |
|-----------|----------|-------|-------|
| career_changer | 37.5 | F | 30.0-52.5 |
| student_non_designer | 52.5 | B | 37.5-77.5 |
| ux_researcher | 72.5 | B | 72.5-72.5 |
| design_leader | 75.0 | B | 70.0-77.5 |
| traditional_craftsperson | 75.0 | B | 75.0-75.0 |
| agency_creative_director | 77.5 | B | 75.0-80.0 |
| ai_native_engineer | 78.8 | B | 77.5-80.0 |
| curious_explorer | 78.8 | B | 77.5-80.0 |
| app_builder | 79.2 | B | 77.5-80.0 |
| daily_user | 87.5 | A+ | 87.5-87.5 |

## Nielsen Heuristic Analysis
**Coverage:** 9/10 heuristics cited | **Citation rate:** 99%

| Heuristic | Count |
|-----------|-------|
| Match Real World | 176 |
| Visibility Of System Status | 133 |
| Recognition Over Recall | 55 |
| Help Documentation | 39 |
| User Control Freedom | 37 |
| Flexibility Efficiency | 16 |
| Consistency Standards | 12 |
| Minimalist Design | 10 |
| Error Prevention | 2 |

**Missing:** error_recovery

## Cognitive Walkthrough Failure Points
**Total failures:** 599 | **Unique pages with failures:** 3

| CW Question | Failure Rate |
|-------------|-------------|
| Will Try Right Effect | 21% |
| Notices Correct Action | 44% |
| Associates Action With Goal | 62% |
| Sees Progress | 11% |

### assess?cohort=think-aloud-test (434 failures)
  Questions failed: sees_progress, will_try_right_effect, notices_correct_action, associates_action_with_goal
  Archetypes: agency_creative_director, career_changer, daily_user, ux_researcher, design_leader, student_non_designer, curious_explorer, ai_native_engineer, traditional_craftsperson, app_builder
  - [design_leader] associates_action_with_goal: The form positions data collection as a gate to evaluation, which signals this tool prioritizes their metrics over my time. That misaligns with my stated need: 'tools that work for my weakest team member.' Weak team members won't tolerate friction.
  - [design_leader] associates_action_with_goal: Here's where I hesitate: the question conflates my personal workflow with what I'm *recommending* for 40 people. As VP, my automation needs are different from my junior designers'. This question doesn't distinguish. I'm not sure if I'm answering for myself or anchoring a team baseline—that ambiguity makes the action-goal connection unclear.
  - [design_leader] associates_action_with_goal: Here's the friction: 'YOUR work' is singular, but I'm thinking about 40 people. My personal automation level might be 4/5, but my junior designers are probably 1/2. For a team rollout assessment, I need to know if this tool works for the 40th percentile or the 90th. The singular framing doesn't give me that insight.

### home (86 failures)
  Questions failed: associates_action_with_goal, sees_progress, notices_correct_action, will_try_right_effect
  Archetypes: agency_creative_director, career_changer, daily_user, ux_researcher, design_leader, student_non_designer, curious_explorer, ai_native_engineer, traditional_craftsperson, app_builder
  - [career_changer] will_try_right_effect: I'm not immediately sure what action I'm supposed to take. There are probably multiple things I could click, and I'm worried I'll pick the wrong one and waste time.
  - [career_changer] notices_correct_action: Without seeing the page, but knowing my anxiety levels — I probably see several options and none of them scream 'START YOUR ASSESSMENT HERE' in a way that makes me confident. I'm reading carefully, which means I'm also second-guessing myself.
  - [career_changer] associates_action_with_goal: Even if I find a button, I need to be sure it actually leads to a self-assessment about AI/UX skills. Job postings use confusing language, and I'm worried this site might too. The button text would need to be really explicit.

### results (79 failures)
  Questions failed: associates_action_with_goal, sees_progress, notices_correct_action, will_try_right_effect
  Archetypes: agency_creative_director, career_changer, daily_user, ux_researcher, design_leader, student_non_designer, app_builder, ai_native_engineer, traditional_craftsperson, curious_explorer
  - [design_leader] will_try_right_effect: Without seeing the actual page, I can't confirm there's a clear path forward. For a team rollout evaluation, I need to know: Can I export results? See cohort patterns? Assign growth paths to others? Those aren't obvious from a blank results page.
  - [design_leader] notices_correct_action: I can't assess button clarity or CTA hierarchy without the accessibility tree. But based on experience, most 'results' pages bury the strategic insights I'd actually need—team-level data, not just individual scores.
  - [design_leader] associates_action_with_goal: My goal is evaluating scalability for 40 people. A single-user results page doesn't signal whether this tool supports batch insights, team comparisons, or administrative workflows. That disconnect is immediate.

## Behavioral Realism
**Events/session:** 29.0 | **Total events:** 1452

| Archetype | Avg Events | Confusion Prob |
|-----------|-----------|----------------|
| design_leader | 53.8 | 0.063 |
| career_changer | 49.6 | 0.364 |
| student_non_designer | 37.2 | 0.321 |
| curious_explorer | 32.2 | 0.269 |
| agency_creative_director | 25.4 | 0.155 |
| traditional_craftsperson | 25.4 | 0.115 |
| ai_native_engineer | 24 | 0.005 |
| ux_researcher | 18.4 | 0.033 |
| app_builder | 15.6 | 0.09 |
| daily_user | 8.8 | 0.111 |

## Usability Issues (by frequency)

### assess?cohort=think-aloud-test (380 mentions)
  Heuristics: match_real_world (170), visibility_of_system_status (63), recognition_over_recall (52), help_documentation (37), user_control_freedom (30), flexibility_efficiency (14), minimalist_design (5), consistency_standards (4), clarity_and_precision (1), clarity_and_progressive_disclosure (1), error_prevention (1)
- Strength: The 'Skip' option gives me control and reduces pressure — I appreciate not being forced to fill everything out. Potential issue: The form doesn't explain *why* these demographics matter or how they're used. For someone anxious like me, a brief note like 'This helps us tailor recommendations' would reduce uncertainty and make me more confident in providing the info.
- The form violates a core principle: it asks for information before revealing the system's value. Users don't know if demographics matter or how they'll be used. 'Optional' softens it but doesn't solve it. For team deployment, this creates a secondary friction point — I'd have to explain to my team why they're being asked for data, and I don't have that answer yet.
- The options are clear and well-written, but they're framed as personal automation levels without context for leaders. For a 40-person design team, my workflow isn't singular—it's distributed. The question lacks flexibility for multi-stakeholder roles. This forces me to choose an option that represents my *personal* use, not my *team's* baseline or my *governance* strategy.

### reflection (85 mentions)
- Results page has no visible content—only action buttons. I had to scroll to find my actual tier placement. This violates basic visibility-of-system-status.
- No visual feedback on option selection during the assessment. Clicking option-item[value='3'] multiple times didn't show `selected: true`, so I assumed clicks failed and kept re-clicking.
- Minor: Question 6 asks about 'automation/reuse level' but the language shifts mid-scale (option 4 introduces 'Work continues' framing) which created a subtle cognitive bump.

### home (65 mentions)
  Heuristics: visibility_of_system_status (43), minimalist_design (5), user_control_freedom (4), consistency_standards (4), match_real_world (4), help_documentation (2), recognition_over_recall (2), flexibility_efficiency (1)
- Positive: The 'Take the Assessment' button is visually prominent and the label is explicit — it directly matches my intent. I don't have to guess what will happen. Concern: Without seeing the full page content, I'm uncertain if there's critical context (like how long the assessment takes, what it measures, or a reassurance that it's non-judgmental) that I should know before proceeding. As someone anxious about being behind, I want to know what I'm walking into.
- The landing page seems to be missing critical context—I'm looking at navigation and buttons, but I don't see the value proposition or problem statement in the accessibility tree. This violates visibility of system status and match_real_world: a VP arriving cold to this page needs to immediately understand 'what is this?' and 'why should my team care?' before I'm asked to take an assessment.
- Strong: The presence of multiple entry points (button CTA + nav link) respects user agency and prevents dead ends. If someone wants to explore Framework first, they can; if they want to jump straight to assessment, that's also obvious.

### results (38 mentions)
  Heuristics: visibility_of_system_status (26), consistency_standards (4), user_control_freedom (3), match_real_world (2), flexibility_efficiency (1), recognition_over_recall (1), error_prevention (1)
- The critical issue: visibility_of_system_status. I've completed an assessment, but I can't see my results. The page structure with buttons is clear, but the absence of the actual result content breaks the fundamental feedback loop. A results page must show results first, then offer actions. Without the accessibility tree, I can't confirm whether the results are below the fold (scroll issue) or genuinely missing (UX failure).
- Secondary strength: user_control_freedom. The button layout gives me clear choices — I can retake, download, chat, or view cohort data. That's good design for someone like me who values optionality and wants to control the next step. But it assumes I've already seen and understood my results, which I haven't.
- The page lacks visibility_of_system_status. I don't know if the results exist, where they are, or why I'm only seeing action buttons. A well-designed results page should show the result content *first*, prominently, with actions secondary. The current structure — buttons without visible results — violates the principle of showing the user what they came for immediately.

## Question Confusion Analysis

**option-item[value='1']** (53 confusion signals)
  Archetypes affected: agency_creative_director, career_changer, daily_user, ux_researcher, design_leader, student_non_designer, app_builder, curious_explorer
  - Mild frustration mixed with clarity. I'm not confused by the question — I understand the automation spectrum. But it doesn't match my context. I feel 
  - I need to be honest about where I actually am right now. I'm coming from education, not tech. I haven't been using these tools daily. I've probably da
  - The question asks about 'automation level' for 'YOUR work' but I'm looking at six options that all start with 'All work stops' or 'Work continues' — t

**option-item[value='P']** (40 confusion signals)
  Archetypes affected: career_changer, ux_researcher, design_leader, student_non_designer, app_builder, ai_native_engineer, traditional_craftsperson, curious_explorer
  - I'm reading this as: 'How do you handle when AI tools break or produce garbage?' Given my persona — 3 years in AI-native startup, shipping daily, dire
  - I'm noticing I *could* move to I if I invested a few hours writing down what I know. The gap between P and I isn't capability — it's documentation dis
  - This question feels *accurate*. It's not generic—it's asking about how I actually work, not aspirational nonsense. There's something validating about 

**option-item[value='3']** (35 confusion signals)
  Archetypes affected: student_non_designer, ai_native_engineer, app_builder
  - I'm hesitating for maybe 3 seconds because option 5 is seductive (it sounds more advanced), but I'm honest: I don't run autonomous harnesses daily, an
  - Slight friction here. Option 3 feels safe but maybe undersells how much automation I actually rely on (Cursor's inline suggestions, ESLint auto-fix, T
  - Six distinct options arranged as a spectrum from 0–5, each describing a different automation posture. The framing is 'All work stops' for 0–3, then sh

**option-item[value='I']** (34 confusion signals)
  Archetypes affected: agency_creative_director, ux_researcher, design_leader, student_non_designer, ai_native_engineer, traditional_craftsperson, app_builder
  - No visual differentiation between unselected options—they're all equally salient. This is fine for clarity, but doesn't guide me toward the 'right' an
  - I'm torn between P ('always manually verify') and I ('note where AI was used and why outputs were accepted or rejected'). P feels safer — it aligns wi
  - I need to pick where I honestly sit. Looking at my actual behavior: I use AI for ideation brainstorms with my team—I'll prompt it, we'll riff on outpu

**option-item[value='4']** (28 confusion signals)
  Archetypes affected: ai_native_engineer
  - Mild surprise—in a good way. This question actually respects the distinction between 'I prompt Claude to help me' and 'I build multi-agent orchestrati
  - The language in option 4 ('automated agent harnesses', 'eval suites', 'execute autonomously') uses my vocabulary. That's either intentionally respectf
  - Mildly frustrated and validated simultaneously. Frustrated because the assessment *still* doesn't distinguish between prompt-smithing and agent design

**option-item[value='2']** (16 confusion signals)
  Archetypes affected: app_builder, design_leader, ux_researcher, curious_explorer
  - I'm realizing I might be overthinking this. I use AI occasionally, I manually check things — that's option 2. My tendency toward conscientiousness (5/
  - I need to map *my actual work* to one of these levels, not aspirational me. Let me be honest: I use AI occasionally for specific tasks — drafting brie
  - I'm going to read all 6 options carefully because I'm scared of picking wrong and this feels like it's measuring my skill level. Let me map my actual 

**option-item[value='0']** (14 confusion signals)
  Archetypes affected: traditional_craftsperson, career_changer
  - I realize I'm overthinking this. The assessment is asking what MY current work looks like, not what I aspire to. I don't have a full-time UX job yet. 
  - Six clear options arranged vertically, progressing from zero AI use to full automation. The language is precise and unambiguous—'I don't use AI tools 
  - The option language is specific enough that I can't accidentally select the wrong answer. 'All my design work is manual' is unambiguous. No overlap be

**#intakeAge** (9 confusion signals)
  Archetypes affected: ux_researcher, student_non_designer, curious_explorer, career_changer
  - I'm realizing I'm overthinking a simple form. This is typical for me — I read everything carefully, afraid I'll miss something crucial or fill it out 
  - There's a form with optional demographic fields (cohort, age, role) and two buttons: 'Start Assessment' and 'Skip'. The cohort field is already filled
  - The pre-populated cohort field is good UX from a research perspective (reduces friction, ensures data integrity), but it's opaque to me. As a user, I 

## Persona Satisfaction (NPS by archetype)
| Archetype | Avg NPS | Range | Share Rate |
|-----------|---------|-------|------------|
| design_leader | 6.0 | 6-6 | 100% |
| career_changer | 6.3 | 5-7 | 100% |
| agency_creative_director | 7.0 | 7-7 | 100% |
| ai_native_engineer | 7.0 | 7-7 | 100% |
| app_builder | 7.0 | 7-7 | 100% |
| daily_user | 7.0 | 7-7 | 100% |
| student_non_designer | 7.0 | 7-7 | 100% |
| traditional_craftsperson | 7.0 | 7-7 | 100% |
| ux_researcher | 7.0 | 7-7 | 100% |
| curious_explorer | 7.8 | 7-8 | 100% |

## Flow Completion
- Completion rate: 56% (28/50)

## Self-Consistency Convergence
**Overall convergence rate:** 0.0
**Archetypes analyzed:** 10

- **career_changer**: 0 robust / 43 total (0% convergence)
- **design_leader**: 0 robust / 67 total (0% convergence)
- **app_builder**: 0 robust / 55 total (0% convergence)
- **traditional_craftsperson**: 0 robust / 45 total (0% convergence)
- **ux_researcher**: 0 robust / 29 total (0% convergence)
- **curious_explorer**: 0 robust / 58 total (0% convergence)
- **student_non_designer**: 0 robust / 41 total (0% convergence)
- **ai_native_engineer**: 0 robust / 63 total (0% convergence)
- **agency_creative_director**: 0 robust / 54 total (0% convergence)
- **daily_user**: 0 robust / 28 total (0% convergence)

## Notable Self-Awareness Moments
- **career_changer**: I'm noticing my impulse to second-guess myself already — should I read the Framework first? Am I jumping in too fast? This is classic anxious behavior for me. But I also recognize that my job market anxiety is pushing me to just get the assessment done and see where I stand. I'm 0 years in education/tech, and every day I delay feels like falling further behind. The bootcamp is supposed to help me, so maybe I should trust the structure they've provided.
- **career_changer**: I'm realizing I'm overthinking a simple form. This is typical for me — I read everything carefully, afraid I'll miss something crucial or fill it out 'wrong.' The fact that I'm worried about whether demographics are needed tells me I'm still very much in 'outsider' mode in tech. A more experienced person probably wouldn't hesitate here. Also, I notice I haven't seen the actual assessment questions yet, so I'm anxious about what's coming next.
- **design_leader**: I'm doing exactly what my persona says: asking 'what's the team adoption story here?' before I even take the assessment. I'm not the type to jump into an interactive tool without understanding the underlying model. My conscientiousness (5/5) means I'm reading carefully, and my AI comfort level (moderate) means I'm skeptical of hype. I want evidence that this scales, not just that it works for power users.
- **design_leader**: I notice I'm pattern-matching to 100+ tool evaluations I've done. I'm making a quick judgment based on workflow assumptions, not malice toward this designer. But that's exactly the point — enterprise leaders like me are trained to detect friction early because it compounds across teams. I'm being efficient, maybe slightly unfair, but this is how adoption decisions actually get made in the real world.
- **design_leader**: I'm realizing this assessment may be designed for individual contributors, not leaders. My honest answer is awkward: I dabble in option 1 (ChatGPT for ideas) but I'm careful about my team using options 2-3 without guardrails. I'm moderate with AI—I use it, but I'm more focused on *how my team adopts it safely*. I'm not in option 0 (that's not honest) and I'm nowhere near options 4-5 (that assumes autonomous systems, which I'd need to evaluate carefully before deploying).
- **design_leader**: I'm realizing I might be overthinking this. I use AI occasionally, I manually check things — that's option 2. My tendency toward conscientiousness (5/5) means I probably default to 'one more review pass' rather than trusting automation. I should trust my first instinct here rather than spiraling into 'but what does this mean for team adoption?' That's a separate conversation. This question is about my baseline practice, and my baseline is: checklist before integration.
- **design_leader**: I'm realizing this assessment might not be built for design leaders — it's built for individual contributors in software engineering. I have 40 designers at varying skill levels, not individual technical workflows to automate. My concern isn't 'does AI run while I'm away' — it's 'can my junior designer use Figma+AI without breaking our design system' and 'how do I scale adoption without creating quality variance.' This framework feels orthogonal to my actual leadership challenge.
- **design_leader**: I notice I'm rationalizing a bit here — trying to land on the 'mature' option rather than the 'lightweight' one. That's my conscientiousness and leadership mindset showing: I want to model best practices even if my actual daily use is moderate. But the question asks where *I* am, not where I want to be. Honesty is more useful than aspiration for an assessment. I'm genuinely using prompts with some structure, so level 2 is right. Not overthinking this.
- **design_leader**: I'm recognizing that I ask 'Can my junior designers use this?' but this question is about *my* output, not theirs. There's a difference. I probably use AI less intensively than my best designers do, because I spend more time on strategy and less on execution. That's okay. I'm also realizing these options assume a pretty high baseline AI fluency—there's no option for 'I'm experimenting' or 'context-dependent.' Real work is messier. Some projects are 30% AI-assisted, others are 0%. But I have to pick one.
- **design_leader**: I'm realizing I may be more typical than I thought—16 years in enterprise tech, moderate AI comfort, and I'm still at 'save and reuse some prompts.' That's actually a healthy place. I don't need to feel behind. But this scale might create a false sense that everyone should be automating and templating. That's not the bottleneck for most design teams. The bottleneck is helping the junior person on my team feel confident using AI at all. This assessment is measuring sophistication, not readiness or maturity for *teams*.

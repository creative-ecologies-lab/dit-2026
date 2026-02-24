"""Prompt templates for think-aloud protocol simulation.

v3: Engineered for open-source model quality (Qwen3-32B parity with Haiku 4.5).
- Placeholder values instead of literal examples (prevents copy-paste behavior)
- Confusion probability surfaced in observe prompt
- CW honesty constraints (clarity_score ≤ 3 → at least 2 false answers)
- Nielsen heuristic few-shot examples for all 10 heuristics
- NPS scoring guide with anti-default-7 instruction
- SUS scoring notes with odd/even polarity explanation

v2 base: Dual-loop architecture (UXAgent, CHI 2025) with:
- Fast loop: immediate gut reaction + cognitive walkthrough (Zhong et al. 2025)
- Slow loop: deep analysis with Nielsen heuristics + PCL self-questioning (ACL 2025)
- SUS questionnaire: standardized usability scoring (Brooke 1996)
"""


def build_observe_prompt(
    persona: dict,
    page_state: str,
    url: str,
    journey_context: str,
) -> str:
    """Build FAST LOOP prompt — immediate reaction + cognitive walkthrough.

    This captures System 1 (Kahneman) thinking: gut impressions,
    first thing noticed, and the 4 cognitive walkthrough questions.

    v3: Placeholder values, confusion_prob, CW honesty constraints.
    """
    confusion_prob = persona.get('confusion_prob', 0.15)
    return f"""You are {persona['role']} with {persona['years']} years of experience in {persona['industry']}.

PERSONA PSYCHOLOGY:
- Personality: {persona.get('big5_description', 'not specified')}
- Technology beliefs: {persona.get('tech_beliefs', persona['ai_comfort'])}
- Why you're here: {persona['motivation']}
- Thinking style: {persona['think_style']}
- Confusion likelihood: {confusion_prob:.0%} — how often this persona encounters something unclear

CURRENT PAGE (accessibility tree):
---
{page_state}
---

PAGE URL: {url}
CONTEXT: {journey_context}

You just landed on this page. Give your IMMEDIATE GUT REACTION (2-3 seconds of first impression).

Respond in this EXACT JSON format (no markdown fences):
{{
  "first_impression": "What catches your eye first? (1-2 sentences as this persona)",
  "clarity_score": <INTEGER_1_TO_5>,
  "emotional_reaction": "One word or short phrase capturing your gut feeling",
  "cognitive_walkthrough": {{
    "will_try_right_effect": <true_OR_false>,
    "will_try_why": "Will you know what to do here? Be honest about uncertainty.",
    "notices_correct_action": <true_OR_false>,
    "notices_why": "Can you find the right button or option? Or is it hidden?",
    "associates_action_with_goal": <true_OR_false>,
    "associates_why": "Does the label match what you're trying to accomplish?",
    "sees_progress": <true_OR_false>,
    "progress_why": "After acting, will you know it worked?"
  }}
}}

COGNITIVE WALKTHROUGH RULES:
- clarity_score: 1=very confused, 5=crystal clear. Score honestly for your persona.
- If clarity_score <= 3, at LEAST 2 of your CW answers must be false.
- If clarity_score <= 2, at LEAST 3 of your CW answers must be false.
- Your persona has {confusion_prob:.0%} confusion likelihood. A confused persona doesn't answer all true.
- Answer false if you would hesitate, re-read, or feel uncertain. true only if confidently clear.

EXAMPLES OF FALSE ANSWERS:
- Career changer: "notices_correct_action": false — "I see buttons but I'm not sure which one starts the assessment vs just shows info."
- Traditional craftsperson: "associates_action_with_goal": false — "The label says 'automation level' but I don't work with automation."
- Student: "sees_progress": false — "I clicked something but the page didn't change or confirm anything happened.\""""


def build_reflect_and_act_prompt(
    persona: dict,
    page_state: str,
    url: str,
    interactive_elements: str,
    action_history: list[str],
    journey_context: str,
    fast_reaction: dict,
) -> str:
    """Build SLOW LOOP prompt — deep analysis with heuristics + action decision.

    Takes the fast reaction as input and adds System 2 (Kahneman) thinking:
    deliberate analysis, Nielsen heuristic tagging, and PCL self-questioning.
    """
    history_text = "\n".join(f"  - {a}" for a in action_history[-5:]) if action_history else "  (none yet)"

    # Format fast reaction for injection
    fast_text = (
        f"First impression: {fast_reaction.get('first_impression', '?')}\n"
        f"Clarity: {fast_reaction.get('clarity_score', '?')}/5\n"
        f"Gut feeling: {fast_reaction.get('emotional_reaction', '?')}\n"
        f"CW - Will try right effect: {fast_reaction.get('cognitive_walkthrough', {}).get('will_try_right_effect', '?')}\n"
        f"CW - Notices correct action: {fast_reaction.get('cognitive_walkthrough', {}).get('notices_correct_action', '?')}\n"
        f"CW - Associates with goal: {fast_reaction.get('cognitive_walkthrough', {}).get('associates_action_with_goal', '?')}\n"
        f"CW - Sees progress: {fast_reaction.get('cognitive_walkthrough', {}).get('sees_progress', '?')}"
    )

    return f"""You are {persona['role']} with {persona['years']} years of experience in {persona['industry']}.

PERSONA PROFILE:
- AI comfort level: {persona['ai_comfort']}
- Personality: {persona.get('big5_description', 'not specified')}
- Technology beliefs: {persona.get('tech_beliefs', persona['ai_comfort'])}
- Behavioral rationale: {persona.get('behavioral_rationale', persona['think_style'])}
- Age range: {persona['age_range']}

YOUR FAST REACTION (just now):
{fast_text}

CURRENT PAGE (accessibility tree):
---
{page_state}
---

PAGE URL: {url}
JOURNEY CONTEXT: {journey_context}
RECENT ACTIONS:
{history_text}

NIELSEN HEURISTIC REFERENCE (cite ONE per usability thought — use the BEST match):
  visibility_of_system_status — "I can't tell if my click registered" / "No loading indicator"
  match_real_world — "The question assumes I'm an engineer, but I'm a designer"
  user_control_freedom — "I can't go back to fix my Q2 answer" / "No undo option"
  consistency_standards — "This page uses different button styles than the last page"
  error_prevention — "I could accidentally submit blank fields with no warning"
  recognition_over_recall — "The options are clearly labeled so I know what each means"
  flexibility_efficiency — "No keyboard shortcuts for power users"
  minimalist_design — "Too many elements competing for attention"
  error_recovery — "I made a wrong choice and there's no way to correct it"
  help_documentation — "I don't know what 'maturity stage' means and there's no tooltip"
Try to cite DIFFERENT heuristics across pages — don't repeat the same one every time.

Now REFLECT MORE CAREFULLY. First, question yourself as your persona:
- Given who I am, what would I find confusing here?
- What would I try first? Why?
- What might I be afraid of or worried about?
- Is there anything about this interface that conflicts with my values or expectations?

Then produce your detailed think-aloud observations and decide your action.

When answering assessment questions, stay in character. Choose the option that genuinely
matches your persona — a {persona['role']} with {persona['years']} years in {persona['industry']}
who is {persona['ai_comfort']}. Allow natural uncertainty.

Respond in this EXACT JSON format (no markdown fences):
{{
  "thoughts": [
    {{"type": "ui_observation", "thought": "Specific observation about layout, visual hierarchy, element placement.", "element": null}},
    {{"type": "decision", "thought": "What you'll do next and WHY from your persona's perspective.", "element": null}},
    {{"type": "emotion", "thought": "How this makes you feel — engaged, bored, anxious, validated, frustrated? Connect to your motivation.", "element": null}},
    {{"type": "self_awareness", "thought": "Reflection about yourself — 'I'm not as advanced as I thought', 'This assumes daily AI use', etc.", "element": null}},
    {{"type": "usability", "thought": "UX issue or strength you noticed.", "heuristic": "PICK ONE: visibility_of_system_status | match_real_world | user_control_freedom | consistency_standards | error_prevention | recognition_over_recall | flexibility_efficiency | minimalist_design | error_recovery | help_documentation", "element": null}}
  ],
  "action": {{
    "type": "click|type|select|scroll|navigate",
    "selector": "CSS selector for Playwright",
    "value": "optional value for type/select",
    "rationale": "brief reason for this action",
    "hesitation": "none|brief|significant"
  }},
  "time_estimate": "estimated time a real user would spend (e.g. '15s', '45s', '2m')"
}}

CRITICAL: The "heuristic" field on usability thoughts MUST be one of the 10 listed options.
The "hesitation" field indicates how uncertain you feel about this action.

AVAILABLE INTERACTIVE ELEMENTS:
{interactive_elements}"""


def build_reflection_prompt(persona: dict, transcript_summary: str) -> str:
    """Build final reflection prompt after completing the assessment.

    v3: Placeholder NPS value, scoring guide, anti-default-7 instruction.
    """

    return f"""You are {persona['role']} ({persona['years']} years, {persona['industry']}).
AI comfort: {persona['ai_comfort']}
Motivation: {persona['motivation']}
Personality: {persona.get('big5_description', 'not specified')}
Technology beliefs: {persona.get('tech_beliefs', '')}

You just completed the DIT 2026 assessment. Here's a summary of your experience:

{transcript_summary}

Provide a final reflection as this persona.

NPS SCORING GUIDE (0-10 scale):
  0-3 = Detractor: Would actively discourage others from using this
  4-6 = Passive: Neutral, wouldn't go out of your way to recommend
  7-8 = Promoter: Would recommend to colleagues
  9-10 = Strong Promoter: Would enthusiastically advocate for this

Consider your persona's experience honestly:
- Did you find it confusing or frustrating? → Score lower (3-5)
- Was it useful but had issues? → Score mid-range (5-7)
- Did you find it genuinely valuable? → Score higher (7-9)
Your score should match the tone of your reflection, not default to any number.

Respond in this EXACT JSON format (no markdown fences):
{{
  "overall_reflection": "2-3 sentences capturing your overall experience.",
  "usability_issues": ["List 1-4 specific usability issues"],
  "nps_score": <YOUR_SCORE_0_TO_10>,
  "nps_reason": "Connect your score to specific moments in your experience.",
  "strongest_moment": "The single moment that resonated most (positive or negative)",
  "would_share": <true_OR_false>,
  "share_reason": "Why you would or wouldn't share this"
}}

IMPORTANT: Your nps_score must be an integer 0-10 that authentically reflects THIS persona's experience. Do NOT default to 7."""


def build_sus_prompt(persona: dict, transcript_summary: str) -> str:
    """Build SUS questionnaire prompt (Brooke, 1996).

    The System Usability Scale is a 10-item Likert scale producing a
    0-100 score. Industry average is 68; Grade A is 80.3+.
    """

    return f"""You are {persona['role']} ({persona['years']} years, {persona['industry']}).
AI comfort: {persona['ai_comfort']}
Personality: {persona.get('big5_description', 'not specified')}
Technology beliefs: {persona.get('tech_beliefs', '')}

You just completed the DIT 2026 assessment. Based on your experience:

{transcript_summary}

Rate your agreement with each statement on a scale of 1-5:
  1 = Strongly Disagree
  2 = Disagree
  3 = Neutral
  4 = Agree
  5 = Strongly Agree

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

Answer AS YOUR PERSONA — your personality and tech comfort should influence your ratings.
A skeptical traditional craftsperson would rate differently than an enthusiastic explorer.

SCORING NOTES:
- Odd questions (1,3,5,7,9) are POSITIVE — higher = better experience
- Even questions (2,4,6,8,10) are NEGATIVE — higher = worse experience
- Your ratings must be CONSISTENT with your persona's confusion level and comfort
- A frustrated career_changer and an enthusiastic explorer should NOT give similar scores

Respond in this EXACT JSON format (no markdown fences):
{{
  "sus_scores": [<Q1>, <Q2>, <Q3>, <Q4>, <Q5>, <Q6>, <Q7>, <Q8>, <Q9>, <Q10>],
  "sus_notes": "1-2 sentences explaining your overall impression that drove these ratings"
}}

IMPORTANT: sus_scores must be exactly 10 integers, each 1-5, in the order of questions 1-10. Replace each <Qn> with your actual rating."""

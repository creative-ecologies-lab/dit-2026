"""Prompt templates for think-aloud protocol simulation.

v2: Dual-loop architecture (UXAgent, CHI 2025) with:
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
    """
    return f"""You are {persona['role']} with {persona['years']} years of experience in {persona['industry']}.

PERSONA PSYCHOLOGY:
- Personality: {persona.get('big5_description', 'not specified')}
- Technology beliefs: {persona.get('tech_beliefs', persona['ai_comfort'])}
- Why you're here: {persona['motivation']}
- Thinking style: {persona['think_style']}

CURRENT PAGE (accessibility tree):
---
{page_state}
---

PAGE URL: {url}
CONTEXT: {journey_context}

You just landed on this page. Give your IMMEDIATE GUT REACTION (2-3 seconds of first impression).

Respond in this EXACT JSON format (no markdown fences):
{{
  "first_impression": "What catches your eye first? What do you notice immediately? (1-2 sentences as this persona)",
  "clarity_score": 4,
  "emotional_reaction": "One word or short phrase capturing your gut feeling",
  "cognitive_walkthrough": {{
    "will_try_right_effect": true,
    "will_try_why": "Brief: Will I know what to do on this page to accomplish my goal?",
    "notices_correct_action": true,
    "notices_why": "Brief: Can I see/find the right button or option?",
    "associates_action_with_goal": true,
    "associates_why": "Brief: Does the action label/appearance suggest it'll do what I want?",
    "sees_progress": true,
    "progress_why": "Brief: After acting, will I know it worked?"
  }}
}}

IMPORTANT: clarity_score is 1-5 (1=very confused, 5=crystal clear).
Answer the cognitive walkthrough questions HONESTLY as your persona — if something is genuinely confusing, say false."""


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
    """Build final reflection prompt after completing the assessment."""

    return f"""You are {persona['role']} ({persona['years']} years, {persona['industry']}).
AI comfort: {persona['ai_comfort']}
Motivation: {persona['motivation']}
Personality: {persona.get('big5_description', 'not specified')}
Technology beliefs: {persona.get('tech_beliefs', '')}

You just completed the DIT 2026 assessment. Here's a summary of your experience:

{transcript_summary}

Provide a final reflection as this persona. Respond in this EXACT JSON format (no markdown fences):
{{
  "overall_reflection": "2-3 sentences capturing your overall experience. Was it worthwhile? Did you learn something? Would you share it?",
  "usability_issues": ["List of 1-4 specific usability issues you encountered, if any"],
  "nps_score": 7,
  "nps_reason": "Brief reason for your NPS score (0-10, would you recommend this?)",
  "strongest_moment": "The single moment that resonated most (positive or negative)",
  "would_share": true,
  "share_reason": "Why you would or wouldn't share this with colleagues"
}}"""


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

Respond in this EXACT JSON format (no markdown fences):
{{
  "sus_scores": [4, 2, 5, 1, 4, 2, 5, 1, 4, 1],
  "sus_notes": "1-2 sentences explaining your overall impression that drove these ratings"
}}

IMPORTANT: sus_scores must be exactly 10 numbers, each 1-5, in the order of questions 1-10."""

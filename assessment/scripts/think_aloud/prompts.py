"""Prompt templates for think-aloud protocol simulation."""


def build_observe_and_act_prompt(
    persona: dict,
    page_state: str,
    url: str,
    interactive_elements: str,
    action_history: list[str],
    journey_context: str,
) -> str:
    """Build combined observation + action prompt for a single page state."""

    history_text = "\n".join(f"  - {a}" for a in action_history[-5:]) if action_history else "  (none yet)"

    return f"""You are {persona['role']} with {persona['years']} years of experience in {persona['industry']}.

PERSONA PROFILE:
- AI comfort level: {persona['ai_comfort']}
- Why you're here: {persona['motivation']}
- Your thinking style: {persona['think_style']}
- Age range: {persona['age_range']}

You are performing a THINK-ALOUD PROTOCOL while using a web assessment tool called
"DIT 2026 — What Kind of AI-Augmented Designer Are You?" This tool was shared by
design leader John Maeda to help people understand their relationship with AI in design work.

CURRENT PAGE (accessibility tree):
---
{page_state}
---

PAGE URL: {url}
JOURNEY CONTEXT: {journey_context}
RECENT ACTIONS:
{history_text}

Think aloud about what you see, then decide what to do next. You MUST produce ALL FIVE
thought categories and ONE action decision.

When answering assessment questions, stay in character. Choose the option that genuinely
matches your persona — a {persona['role']} with {persona['years']} years in {persona['industry']}
who is {persona['ai_comfort']}. Allow natural uncertainty — you might over- or under-estimate
yourself, or hesitate between two options. That's realistic.

Respond in this EXACT JSON format (no markdown fences):
{{
  "thoughts": [
    {{"type": "ui_observation", "thought": "What you notice about the page layout, elements, visual hierarchy. Be specific about what's clear or confusing.", "element": null}},
    {{"type": "decision", "thought": "What you'll do next and WHY, connected to your background and experience. If answering a question, explain your reasoning.", "element": null}},
    {{"type": "emotion", "thought": "How this page/moment makes you feel. Engaged? Bored? Anxious? Validated? Frustrated? Connect to your motivation.", "element": null}},
    {{"type": "self_awareness", "thought": "Any moment of reflection about yourself. 'I'm not as advanced as I thought', 'This question assumes daily AI use', 'I recognize myself here'.", "element": null}},
    {{"type": "usability", "thought": "UX observations — navigation clarity, wording issues, missing affordances, good design moments, accessibility, mobile concerns.", "element": null}}
  ],
  "action": {{
    "type": "click|type|select|scroll|navigate",
    "selector": "CSS selector or element description for Playwright",
    "value": "optional value for type/select",
    "rationale": "brief reason for this action"
  }},
  "time_estimate": "estimated time a real user would spend on this page (e.g. '15s', '45s', '2m')"
}}

AVAILABLE INTERACTIVE ELEMENTS:
{interactive_elements}
"""


def build_reflection_prompt(persona: dict, transcript_summary: str) -> str:
    """Build final reflection prompt after completing the assessment."""

    return f"""You are {persona['role']} ({persona['years']} years, {persona['industry']}).
AI comfort: {persona['ai_comfort']}
Motivation: {persona['motivation']}

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
}}
"""

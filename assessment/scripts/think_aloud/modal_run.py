"""Modal parallel think-aloud: 50 sessions at max speed.

Runs each think-aloud session in its own Modal container (1 Chromium browser,
1 async Anthropic client). All 50 sessions execute simultaneously — total
wall-clock time ~5 minutes instead of ~3 hours sequential.

Usage:
    # One-time setup
    pip install modal
    modal setup
    modal secret create anthropic-key ANTHROPIC_API_KEY=sk-ant-...

    # Run all 50 sessions in parallel
    cd assessment
    modal run scripts.think_aloud.modal_run

    # Custom args
    modal run scripts.think_aloud.modal_run --sessions 50 --seed 42 --budget 20
"""

import modal

app = modal.App("think-aloud-v2")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("anthropic>=0.40", "playwright>=1.49")
    .run_commands("playwright install --with-deps chromium")
)

# ── All constants (inlined from config.py) ──

PROTOCOL_VERSION = "2.0"
DEFAULT_TARGET = "https://dit-maeda.noahratzan.com"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_COHORT = "think-aloud-test"
INPUT_COST_PER_MTOK = 3.0
OUTPUT_COST_PER_MTOK = 15.0
WAIT_AFTER_CLICK_MS = 600
PAGE_LOAD_TIMEOUT_MS = 30000
HESITATION_DELAY_MS = 2000
REREAD_DELAY_MS = 1500
MISCLICK_RECOVERY_MS = 800
SUS_GRADE_THRESHOLDS = {
    "A+": 84.1, "A": 80.3, "B": 68.0, "C": 51.0, "D": 35.7, "F": 0.0,
}


# ── Prompt builders (inlined from prompts.py) ──

def build_observe_prompt(persona, page_state, url, journey_context):
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


def build_reflect_and_act_prompt(persona, page_state, url, interactive_elements,
                                  action_history, journey_context, fast_reaction):
    history_text = "\n".join(f"  - {a}" for a in action_history[-5:]) if action_history else "  (none yet)"
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


def build_reflection_prompt(persona, transcript_summary):
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


def build_sus_prompt(persona, transcript_summary):
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


# ── Driver functions (inlined from driver.py) ──

def _flatten_a11y_tree(node, depth=0, max_depth=5):
    if depth > max_depth:
        return ""
    indent = "  " * depth
    role = node.get("role", "")
    name = node.get("name", "")
    value = node.get("value", "")
    if role in ("none", "generic", "presentation") and not name:
        parts = []
        for child in node.get("children", []):
            parts.append(_flatten_a11y_tree(child, depth, max_depth))
        return "\n".join(p for p in parts if p)
    line = f"{indent}[{role}]"
    if name:
        line += f' "{name}"'
    if value:
        line += f" value={value}"
    for key in ("checked", "selected", "disabled", "expanded", "pressed"):
        if key in node:
            line += f" {key}={node[key]}"
    parts = [line]
    for child in node.get("children", []):
        child_text = _flatten_a11y_tree(child, depth + 1, max_depth)
        if child_text:
            parts.append(child_text)
    return "\n".join(parts)


INTERACTIVE_JS = """() => {
    const elements = [];
    document.querySelectorAll('button, a.btn, [role="button"]').forEach(el => {
        if (el.offsetParent !== null) {
            elements.push({
                tag: el.tagName.toLowerCase(),
                text: el.textContent.trim().substring(0, 80),
                id: el.id || null,
                classes: el.className.substring(0, 100),
                href: el.href || null,
            });
        }
    });
    document.querySelectorAll('label.option-item').forEach(el => {
        if (el.offsetParent !== null) {
            const input = el.querySelector('input');
            elements.push({
                tag: 'option-item',
                text: el.textContent.trim().substring(0, 120),
                value: input ? input.value : null,
                name: input ? input.name : null,
                selected: el.classList.contains('selected'),
            });
        }
    });
    document.querySelectorAll('input:not([type="radio"]):not([type="hidden"]), select, textarea').forEach(el => {
        if (el.offsetParent !== null) {
            elements.push({
                tag: el.tagName.toLowerCase(),
                type: el.type || null,
                id: el.id || null,
                value: el.value || null,
                placeholder: el.placeholder || null,
            });
        }
    });
    document.querySelectorAll('.nav-links a').forEach(el => {
        elements.push({
            tag: 'nav-link',
            text: el.textContent.trim(),
            href: el.href,
            active: el.classList.contains('active'),
        });
    });
    return elements;
}"""

STAGE_JS = """() => {
    if (document.querySelector('#intakeStage') &&
        document.querySelector('#intakeStage').style.display !== 'none')
        return 'intake';
    if (document.querySelector('#saeStage') &&
        document.querySelector('#saeStage').style.display !== 'none')
        return 'sae';
    if (document.querySelector('#epiasStage') &&
        document.querySelector('#epiasStage').style.display !== 'none')
        return 'epias';
    if (document.querySelector('#loadingStage') &&
        document.querySelector('#loadingStage').style.display !== 'none')
        return 'loading';
    if (document.querySelector('#completedStage') &&
        document.querySelector('#completedStage').style.display !== 'none')
        return 'completed';
    return 'unknown';
}"""


async def get_page_state(page):
    import json as _json
    try:
        a11y = await page.accessibility.snapshot()
        a11y_text = _flatten_a11y_tree(a11y) if a11y else "(empty page)"
    except Exception:
        a11y_text = "(accessibility tree unavailable)"
    if len(a11y_text) > 6000:
        a11y_text = a11y_text[:6000] + "\n... (truncated)"
    interactive = await page.evaluate(INTERACTIVE_JS)
    interactive_text = _json.dumps(interactive, indent=2) if interactive else "(no interactive elements found)"
    if len(interactive_text) > 3000:
        interactive_text = interactive_text[:3000] + "\n... (truncated)"
    return {"a11y_text": a11y_text, "url": page.url, "interactive_elements": interactive_text}


async def execute_action(page, action):
    action_type = action.get("type", "click")
    selector = action.get("selector", "")
    value = action.get("value", "")
    try:
        if action_type == "click":
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(WAIT_AFTER_CLICK_MS)
        elif action_type == "type":
            await page.fill(selector, value, timeout=5000)
        elif action_type == "select":
            await page.select_option(selector, value, timeout=5000)
        elif action_type == "navigate":
            target = value or selector
            if not target.startswith("http"):
                base = page.url.rsplit("/", 1)[0] if "/" in page.url else page.url
                target = base.rstrip("/") + "/" + target.lstrip("/")
            await page.goto(target, timeout=PAGE_LOAD_TIMEOUT_MS, wait_until="networkidle")
        elif action_type == "scroll":
            await page.evaluate("window.scrollBy(0, 400)")
            await page.wait_for_timeout(300)
    except Exception as e:
        return f"Action failed: {e}"
    return None


# ── Engine (async only, inlined from engine.py) ──

def _parse_json(text):
    import json as _json
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return _json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return _json.loads(text[start:end])
            except Exception:
                pass
        return {"error": "Failed to parse LLM response", "raw": text[:500]}


class BudgetExceeded(Exception):
    pass


class AsyncEngine:
    """Lightweight async-only engine for Modal containers."""

    def __init__(self, model, budget):
        import anthropic
        self.client = anthropic.AsyncAnthropic()
        self.model = model
        self.budget = budget
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

    @property
    def cost_usd(self):
        return (
            self.total_input_tokens * INPUT_COST_PER_MTOK / 1_000_000
            + self.total_output_tokens * OUTPUT_COST_PER_MTOK / 1_000_000
        )

    async def _call(self, prompt, max_tokens=1200):
        if self.cost_usd >= self.budget:
            raise BudgetExceeded(f"${self.cost_usd:.2f} / ${self.budget:.2f}")
        response = await self.client.messages.create(
            model=self.model, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens
        self.call_count += 1
        return response.content[0].text

    async def observe_fast(self, persona, page_state, url, journey_context):
        raw = await self._call(build_observe_prompt(persona, page_state, url, journey_context), 500)
        return _parse_json(raw)

    async def reflect_and_act(self, persona, page_state, url, interactive_elements,
                               action_history, journey_context, fast_reaction):
        raw = await self._call(build_reflect_and_act_prompt(
            persona, page_state, url, interactive_elements,
            action_history, journey_context, fast_reaction,
        ), 1200)
        return _parse_json(raw)

    async def reflect(self, persona, transcript_summary):
        raw = await self._call(build_reflection_prompt(persona, transcript_summary), 600)
        return _parse_json(raw)

    async def score_sus(self, persona, transcript_summary):
        raw = await self._call(build_sus_prompt(persona, transcript_summary), 300)
        result = _parse_json(raw)
        scores = result.get("sus_scores", [])
        if len(scores) == 10 and all(isinstance(s, (int, float)) for s in scores):
            odd = sum(scores[i] for i in range(0, 10, 2))
            even = sum(scores[i] for i in range(1, 10, 2))
            total = max(0, min(100, ((odd - 5) + (25 - even)) * 2.5))
            grade = "F"
            for g, t in sorted(SUS_GRADE_THRESHOLDS.items(), key=lambda x: -x[1]):
                if total >= t:
                    grade = g
                    break
            result["sus_total"] = round(total, 1)
            result["sus_grade"] = grade
        else:
            result["sus_total"] = None
            result["sus_grade"] = None
        return result


# ── The Modal function: 1 container = 1 session ──

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("anthropic-key")],
    timeout=600,
    memory=1024,
    retries=1,
)
async def run_one_session(
    persona: dict,
    session_num: int,
    total_sessions: int,
    target_url: str,
    cohort: str,
    model: str,
    seed: int,
    budget_per_session: float,
) -> dict:
    """Run a single think-aloud session inside a Modal container.

    Returns the full session dict (same schema as local recorder.save()).
    """
    import json as _json
    import random
    import uuid
    from datetime import datetime, timezone
    from playwright.async_api import async_playwright

    rng = random.Random(seed + session_num)
    session_id = str(uuid.uuid4())[:8]
    archetype = persona["archetype_id"]
    prefix = f"[{session_num+1}/{total_sessions}] {archetype}"
    print(f"{prefix}: Starting session {session_id}")

    engine = AsyncEngine(model=model, budget=budget_per_session)

    # Session data accumulator (replaces SessionRecorder)
    pages = []
    action_history = []
    behavioral_events_all = []
    reflection = {}
    result_data = {}
    sus_data = {}
    started_at = datetime.now(timezone.utc).isoformat()

    def record_page(url, llm_response, fast_reaction=None, b_events=None):
        thoughts = llm_response.get("thoughts", [])
        action = llm_response.get("action", {})
        desc = f"{action.get('type', '?')} on {action.get('selector', '?')}"
        if action.get("value"):
            desc += f" = {action['value']}"
        action_history.append(desc)
        rec = {"url": url, "thoughts": thoughts, "action": action,
               "time_estimate": llm_response.get("time_estimate", "unknown")}
        if fast_reaction:
            rec["fast_reaction"] = {
                "first_impression": fast_reaction.get("first_impression"),
                "clarity_score": fast_reaction.get("clarity_score"),
                "emotional_reaction": fast_reaction.get("emotional_reaction"),
                "cognitive_walkthrough": fast_reaction.get("cognitive_walkthrough", {}),
            }
            rec["hesitation"] = action.get("hesitation", "none")
        if b_events:
            rec["behavioral_events"] = b_events
            for ev in b_events:
                behavioral_events_all.append({"event": ev, "url": url})
        pages.append(rec)

    def transcript_summary():
        lines = []
        for i, p in enumerate(pages):
            url = p["url"].split("/")[-1] or "home"
            lines.append(f"Page {i+1} ({url}):")
            fr = p.get("fast_reaction")
            if fr:
                lines.append(f"  [first impression] {fr.get('first_impression', '?')}")
                lines.append(f"  [clarity] {fr.get('clarity_score', '?')}/5 | "
                             f"feeling: {fr.get('emotional_reaction', '?')}")
            for t in p.get("thoughts", []):
                lines.append(f"  [{t['type']}] {t['thought'][:120]}")
            act = p.get("action", {})
            hes = p.get("hesitation", "none")
            lines.append(f"  -> Action: {act.get('type', '?')} {act.get('selector', '')} "
                         f"(hesitation: {hes})")
            evts = p.get("behavioral_events", [])
            if evts:
                lines.append(f"  [behavior] {', '.join(evts)}")
        if result_data:
            lines.append(f"\nResult: SAE L{result_data.get('sae_level', '?')}, "
                         f"EPIAS {result_data.get('epias_stage', '?')}")
        return "\n".join(lines)

    # ── Dual-loop helper ──
    async def dual_loop(page, journey_context):
        state = await get_page_state(page)
        b_events = []
        fast_rx = await engine.observe_fast(persona, state["a11y_text"], state["url"], journey_context)
        # Reading speed delay
        spd = persona.get("reading_speed", 1.0)
        if spd > 1.0:
            await page.wait_for_timeout(int(REREAD_DELAY_MS * (spd - 1.0)))
            b_events.append("slow_reader_delay")
        response = await engine.reflect_and_act(
            persona, state["a11y_text"], state["url"],
            state["interactive_elements"], action_history,
            journey_context, fast_rx,
        )
        hes = response.get("action", {}).get("hesitation", "none")
        if hes == "significant":
            await page.wait_for_timeout(HESITATION_DELAY_MS)
            b_events.extend(["significant_hesitation", "re_read"])
        elif hes == "brief":
            await page.wait_for_timeout(HESITATION_DELAY_MS // 3)
            b_events.append("brief_hesitation")
        record_page(state["url"], response, fast_reaction=fast_rx,
                     b_events=b_events if b_events else None)
        return response, fast_rx, b_events

    # ── Run the session ──
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="ThinkAloud-DIT/2.0-Modal",
        )
        page = await context.new_page()

        try:
            # Landing page
            await page.goto(target_url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
            await page.evaluate("sessionStorage.clear()")
            await dual_loop(page, "You just arrived at the landing page. You're here to take the self-assessment.")
            print(f"{prefix}: Landing page observed")

            # Navigate to assessment
            await page.goto(f"{target_url}/assess?cohort={cohort}",
                            wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
            await page.evaluate("sessionStorage.clear()")

            # Intake
            skip_intake = archetype == "ai_native_engineer" and rng.random() < 0.15
            await dual_loop(page, "You're on the intake page. Fill in optional demographics or skip to start.")
            if skip_intake:
                try:
                    await page.click("#intakeSkip", timeout=3000)
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
                print(f"{prefix}: Intake SKIPPED")
            else:
                try:
                    await page.fill("#intakeCohort", cohort, timeout=3000)
                    if persona.get("age_range"):
                        await page.select_option("#intakeAge", persona["age_range"], timeout=3000)
                    await page.fill("#intakeRole", persona["role"], timeout=3000)
                    await page.click("#intakeStart", timeout=3000)
                    await page.wait_for_timeout(500)
                except Exception:
                    try:
                        await page.click("#intakeSkip", timeout=3000)
                        await page.wait_for_timeout(500)
                    except Exception:
                        pass
                print(f"{prefix}: Intake completed")

            # SAE Questions (6)
            epias_letters = ["E", "P", "I", "A", "S"]
            for q_idx in range(6):
                await page.wait_for_timeout(300)
                stage = await page.evaluate(STAGE_JS)
                if stage != "sae":
                    break
                response, _, _ = await dual_loop(
                    page, f"SAE Question {q_idx+1} of 6. Pick the automation level that best describes YOUR work.")
                action = response.get("action", {})
                # Misclick
                if rng.random() < persona.get("confusion_prob", 0):
                    try:
                        cv = action.get("value", "")
                        if cv.isdigit():
                            wv = str(max(0, min(5, int(cv) + rng.choice([-1, 1]))))
                            await page.click(f'label.option-item:has(input[value="{wv}"])', timeout=2000)
                            await page.wait_for_timeout(MISCLICK_RECOVERY_MS)
                            behavioral_events_all.append({"event": "misclick_corrected", "url": page.url})
                    except Exception:
                        pass
                err = await execute_action(page, action)
                if err:
                    sae_val = max(0, min(5, round(rng.gauss(persona["sae_center"], persona["sae_spread"]))))
                    try:
                        await page.click(f'label.option-item:has(input[value="{sae_val}"])', timeout=3000)
                        await page.wait_for_timeout(WAIT_AFTER_CLICK_MS)
                    except Exception:
                        pass
                print(f"{prefix}: SAE Q{q_idx+1} answered")

            # Wait for EPIAS stage
            try:
                await page.wait_for_selector("#epiasStage", state="visible", timeout=5000)
            except Exception:
                pass

            # EPIAS Questions (5)
            for q_idx in range(5):
                await page.wait_for_timeout(300)
                stage = await page.evaluate(STAGE_JS)
                if stage not in ("epias", "sae"):
                    break
                response, _, _ = await dual_loop(
                    page, f"EPIAS Question {q_idx+1} of 5. Pick the maturity stage that best describes HOW you work.")
                action = response.get("action", {})
                # Misclick
                if rng.random() < persona.get("confusion_prob", 0):
                    try:
                        cv = action.get("value", "")
                        if cv in epias_letters:
                            idx = epias_letters.index(cv)
                            wi = max(0, min(4, idx + rng.choice([-1, 1])))
                            await page.click(f'label.option-item:has(input[value="{epias_letters[wi]}"])', timeout=2000)
                            await page.wait_for_timeout(MISCLICK_RECOVERY_MS)
                            behavioral_events_all.append({"event": "misclick_corrected", "url": page.url})
                    except Exception:
                        pass
                err = await execute_action(page, action)
                if err:
                    idx = max(0, min(4, round(rng.gauss(persona["epias_center"] - 1, persona["epias_spread"]))))
                    try:
                        await page.click(f'label.option-item:has(input[value="{epias_letters[idx]}"])', timeout=3000)
                        await page.wait_for_timeout(WAIT_AFTER_CLICK_MS)
                    except Exception:
                        pass
                print(f"{prefix}: EPIAS Q{q_idx+1} answered")

            # Wait for results
            try:
                await page.wait_for_url("**/results**", timeout=10000)
            except Exception:
                try:
                    await page.click("text=See Results", timeout=3000)
                    await page.wait_for_url("**/results**", timeout=10000)
                except Exception:
                    pass
            await page.wait_for_timeout(1000)

            # Results page
            await dual_loop(page, "You're viewing your results. React to your placement and the growth path suggestions.")
            try:
                rj = await page.evaluate("sessionStorage.getItem('ditResult')")
                if rj:
                    result_data.update(_json.loads(rj))
            except Exception:
                pass
            print(f"{prefix}: Results observed")

            # Reflection + SUS
            summary = transcript_summary()
            reflection.update(await engine.reflect(persona, summary))
            print(f"{prefix}: Reflection generated")

            sus_data.update(await engine.score_sus(persona, summary))
            print(f"{prefix}: SUS scored: {sus_data.get('sus_total', '?')} "
                  f"(Grade {sus_data.get('sus_grade', '?')})")

        except BudgetExceeded as e:
            print(f"{prefix}: Budget exceeded: {e}")
        except Exception as e:
            print(f"{prefix}: ERROR: {e}")
        finally:
            await browser.close()

    # Build persona data for output
    persona_out = {
        "archetype": persona["archetype_id"],
        "archetype_name": persona["archetype_name"],
        "role": persona["role"],
        "years": persona["years"],
        "industry": persona["industry"],
        "age_range": persona["age_range"],
        "ai_comfort": persona["ai_comfort"],
        "motivation": persona["motivation"],
    }
    for k in ("big5", "tech_beliefs", "confusion_prob", "reading_speed"):
        if k in persona:
            persona_out[k] = persona[k]

    session_data = {
        "protocol_version": PROTOCOL_VERSION,
        "session_id": session_id,
        "persona": persona_out,
        "journey": "primary",
        "pages": pages,
        "reflection": reflection,
        "result": result_data,
        "sus": sus_data,
        "behavioral_events_summary": {
            "total": len(behavioral_events_all),
            "events": behavioral_events_all,
        },
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "engine_usage": {
            "calls": engine.call_count,
            "input_tokens": engine.total_input_tokens,
            "output_tokens": engine.total_output_tokens,
            "cost_usd": round(engine.cost_usd, 4),
        },
    }

    print(f"{prefix}: Done | cost=${engine.cost_usd:.3f} | "
          f"SUS={sus_data.get('sus_total', '?')} | NPS={reflection.get('nps_score', '?')}")
    return session_data


# ── Local entrypoint ──

@app.local_entrypoint()
def main(
    sessions: int = 50,
    seed: int = 42,
    budget: float = 20.0,
    target: str = DEFAULT_TARGET,
    cohort: str = DEFAULT_COHORT,
    model: str = DEFAULT_MODEL,
):
    import json as _json
    import sys
    from pathlib import Path

    # Generate personas locally
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from scripts.think_aloud.personas import ARCHETYPES, instantiate_personas
    from scripts.think_aloud.analyzer import load_sessions, analyze, write_report

    output_dir = str(Path(__file__).resolve().parent / "output")
    sessions_dir = Path(output_dir) / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Build persona list
    n_per = max(1, sessions // len(ARCHETYPES))
    remainder = sessions - n_per * len(ARCHETYPES)
    personas = instantiate_personas(n_per_archetype=n_per, seed=seed)
    if remainder > 0:
        extras = instantiate_personas(n_per_archetype=1, seed=seed + 1)
        personas.extend(extras[:remainder])
    personas = personas[:sessions]

    budget_per = budget / len(personas)

    print(f"Modal Think-Aloud v2")
    print(f"  Target: {target}")
    print(f"  Sessions: {len(personas)}")
    print(f"  Model: {model}")
    print(f"  Budget: ${budget:.2f} (${budget_per:.2f}/session)")
    print(f"  Concurrency: {len(personas)} (all at once)")
    print()

    # Fan out all sessions in parallel
    args_list = [
        (p, i, len(personas), target, cohort, model, seed, budget_per)
        for i, p in enumerate(personas)
    ]

    results = []
    total_cost = 0.0
    total_calls = 0
    succeeded = 0
    failed = 0

    for result in run_one_session.starmap(args_list):
        if result and result.get("pages"):
            # Save to local disk
            sid = result["session_id"]
            arch = result["persona"]["archetype"]
            path = sessions_dir / f"{sid}_{arch}.json"
            with open(path, "w", encoding="utf-8") as f:
                _json.dump(result, f, indent=2, ensure_ascii=False)
            results.append(result)
            usage = result.get("engine_usage", {})
            total_cost += usage.get("cost_usd", 0)
            total_calls += usage.get("calls", 0)
            succeeded += 1
            print(f"  Saved: {path.name} | SUS={result.get('sus', {}).get('sus_total', '?')}")
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"RESULTS")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed: {failed}")
    print(f"  Total API calls: {total_calls}")
    print(f"  Total cost: ${total_cost:.2f}")
    print(f"  Cost per session: ${total_cost / max(succeeded, 1):.3f}")
    print()

    # Run analysis on all sessions (including any pre-existing)
    all_sessions = load_sessions(output_dir)
    if all_sessions:
        print(f"Analyzing {len(all_sessions)} sessions...")
        analysis = analyze(all_sessions)
        report_path = write_report(analysis, output_dir)
        print(f"Report: {report_path}")
        s = analysis["summary"]
        print(f"  Avg NPS: {s['avg_nps']} | Std Dev: {s.get('nps_std_dev', '?')}")
        if "sus_analysis" in analysis:
            sus = analysis["sus_analysis"]
            print(f"  Avg SUS: {sus.get('overall_mean', '?')} (Grade {sus.get('overall_grade', '?')})")
        if "heuristic_analysis" in analysis:
            h = analysis["heuristic_analysis"]
            print(f"  Heuristic coverage: {h.get('heuristics_covered', '?')}/10")

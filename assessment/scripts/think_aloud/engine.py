"""LLM think-aloud engine using Claude API.

v2: Dual-loop architecture (fast observe + slow reflect-and-act),
SUS scoring, and self-consistency support.
"""

import asyncio
import json
import threading
import anthropic
from .config import (
    DEFAULT_MODEL, INPUT_COST_PER_MTOK, OUTPUT_COST_PER_MTOK,
    MAX_BUDGET_USD, SUS_GRADE_THRESHOLDS,
)
from .prompts import (
    build_observe_prompt,
    build_reflect_and_act_prompt,
    build_reflection_prompt,
    build_sus_prompt,
)


class ThinkAloudEngine:
    """Manages Claude API calls for think-aloud narration and action decisions."""

    def __init__(self, model: str = DEFAULT_MODEL, budget: float = MAX_BUDGET_USD):
        self.client = anthropic.Anthropic()
        self.async_client = anthropic.AsyncAnthropic()
        self.model = model
        self.budget = budget
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self._lock = asyncio.Lock()  # Protects token counters in parallel mode

    @property
    def cost_usd(self) -> float:
        return (
            self.total_input_tokens * INPUT_COST_PER_MTOK / 1_000_000
            + self.total_output_tokens * OUTPUT_COST_PER_MTOK / 1_000_000
        )

    @property
    def budget_remaining(self) -> float:
        return self.budget - self.cost_usd

    def check_budget(self):
        if self.cost_usd >= self.budget:
            raise BudgetExceeded(
                f"Budget exhausted: ${self.cost_usd:.2f} / ${self.budget:.2f}"
            )

    def _call(self, prompt: str, max_tokens: int = 1200) -> str:
        """Make a single Claude API call (synchronous)."""
        self.check_budget()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens
        self.call_count += 1
        return response.content[0].text

    async def _call_async(self, prompt: str, max_tokens: int = 1200) -> str:
        """Make a single Claude API call (async, for parallel execution)."""
        self.check_budget()
        response = await self.async_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        async with self._lock:
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            self.call_count += 1
        return response.content[0].text

    # ── v1 method (kept for backward compat during transition) ──

    def observe_and_act(
        self,
        persona: dict,
        page_state: str,
        url: str,
        interactive_elements: str,
        action_history: list[str],
        journey_context: str,
    ) -> dict:
        """v1: Combined observation + action in one call."""
        # Build a v1-compatible prompt using the new slow-loop prompt
        # with a synthetic fast reaction
        fast_reaction = {
            "first_impression": "Observing the page",
            "clarity_score": 3,
            "emotional_reaction": "neutral",
            "cognitive_walkthrough": {
                "will_try_right_effect": True,
                "notices_correct_action": True,
                "associates_action_with_goal": True,
                "sees_progress": True,
            },
        }
        prompt = build_reflect_and_act_prompt(
            persona, page_state, url, interactive_elements,
            action_history, journey_context, fast_reaction,
        )
        raw = self._call(prompt, max_tokens=1200)
        return _parse_json(raw)

    # ── v2 dual-loop methods ──

    def observe_fast(
        self,
        persona: dict,
        page_state: str,
        url: str,
        journey_context: str,
    ) -> dict:
        """FAST LOOP: Capture immediate reaction + cognitive walkthrough.

        Quick, reactive observation — System 1 thinking (Kahneman).
        Returns first_impression, clarity_score, emotional_reaction, CW answers.
        """
        prompt = build_observe_prompt(persona, page_state, url, journey_context)
        raw = self._call(prompt, max_tokens=500)
        return _parse_json(raw)

    async def observe_fast_async(
        self,
        persona: dict,
        page_state: str,
        url: str,
        journey_context: str,
    ) -> dict:
        """Async version of observe_fast for parallel execution."""
        prompt = build_observe_prompt(persona, page_state, url, journey_context)
        raw = await self._call_async(prompt, max_tokens=500)
        return _parse_json(raw)

    def reflect_and_act(
        self,
        persona: dict,
        page_state: str,
        url: str,
        interactive_elements: str,
        action_history: list[str],
        journey_context: str,
        fast_reaction: dict,
    ) -> dict:
        """SLOW LOOP: Deep analysis with heuristics + action decision.

        Takes the fast reaction as input and adds deliberate analysis —
        System 2 thinking (Kahneman). Includes Nielsen heuristic tagging,
        PCL self-questioning, and hesitation modeling.
        """
        prompt = build_reflect_and_act_prompt(
            persona, page_state, url, interactive_elements,
            action_history, journey_context, fast_reaction,
        )
        raw = self._call(prompt, max_tokens=1200)
        return _parse_json(raw)

    async def reflect_and_act_async(
        self,
        persona: dict,
        page_state: str,
        url: str,
        interactive_elements: str,
        action_history: list[str],
        journey_context: str,
        fast_reaction: dict,
    ) -> dict:
        """Async version of reflect_and_act for parallel execution."""
        prompt = build_reflect_and_act_prompt(
            persona, page_state, url, interactive_elements,
            action_history, journey_context, fast_reaction,
        )
        raw = await self._call_async(prompt, max_tokens=1200)
        return _parse_json(raw)

    def reflect(self, persona: dict, transcript_summary: str) -> dict:
        """Generate final reflection after assessment completion."""
        prompt = build_reflection_prompt(persona, transcript_summary)
        raw = self._call(prompt, max_tokens=600)
        return _parse_json(raw)

    async def reflect_async(self, persona: dict, transcript_summary: str) -> dict:
        """Async version of reflect for parallel execution."""
        prompt = build_reflection_prompt(persona, transcript_summary)
        raw = await self._call_async(prompt, max_tokens=600)
        return _parse_json(raw)

    def score_sus(self, persona: dict, transcript_summary: str) -> dict:
        """Score the assessment using the System Usability Scale (Brooke 1996).

        Returns 10 Likert scores + computed SUS total (0-100) + grade.
        SUS formula: ((sum_odd_items - 5) + (25 - sum_even_items)) * 2.5
        """
        prompt = build_sus_prompt(persona, transcript_summary)
        raw = self._call(prompt, max_tokens=300)
        result = _parse_json(raw)

        # Compute SUS score from the 10 items
        scores = result.get("sus_scores", [])
        if len(scores) == 10 and all(isinstance(s, (int, float)) for s in scores):
            odd_items = sum(scores[i] for i in range(0, 10, 2))   # Q1,3,5,7,9
            even_items = sum(scores[i] for i in range(1, 10, 2))  # Q2,4,6,8,10
            sus_total = ((odd_items - 5) + (25 - even_items)) * 2.5
            sus_total = max(0, min(100, sus_total))

            # Assign grade
            grade = "F"
            for g, threshold in sorted(SUS_GRADE_THRESHOLDS.items(),
                                       key=lambda x: -x[1]):
                if sus_total >= threshold:
                    grade = g
                    break

            result["sus_total"] = round(sus_total, 1)
            result["sus_grade"] = grade
        else:
            result["sus_total"] = None
            result["sus_grade"] = None

        return result

    async def score_sus_async(self, persona: dict, transcript_summary: str) -> dict:
        """Async version of score_sus for parallel execution."""
        prompt = build_sus_prompt(persona, transcript_summary)
        raw = await self._call_async(prompt, max_tokens=300)
        result = _parse_json(raw)

        scores = result.get("sus_scores", [])
        if len(scores) == 10 and all(isinstance(s, (int, float)) for s in scores):
            odd_items = sum(scores[i] for i in range(0, 10, 2))
            even_items = sum(scores[i] for i in range(1, 10, 2))
            sus_total = ((odd_items - 5) + (25 - even_items)) * 2.5
            sus_total = max(0, min(100, sus_total))

            grade = "F"
            for g, threshold in sorted(SUS_GRADE_THRESHOLDS.items(),
                                       key=lambda x: -x[1]):
                if sus_total >= threshold:
                    grade = g
                    break

            result["sus_total"] = round(sus_total, 1)
            result["sus_grade"] = grade
        else:
            result["sus_total"] = None
            result["sus_grade"] = None

        return result

    def usage_summary(self) -> dict:
        return {
            "calls": self.call_count,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cost_usd": round(self.cost_usd, 4),
            "budget_remaining": round(self.budget_remaining, 4),
        }


class BudgetExceeded(Exception):
    pass


def _parse_json(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Remove markdown code fences
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON within the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"error": "Failed to parse LLM response", "raw": text[:500]}

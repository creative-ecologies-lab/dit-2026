"""LLM think-aloud engine using Claude API."""

import json
import anthropic
from .config import DEFAULT_MODEL, INPUT_COST_PER_MTOK, OUTPUT_COST_PER_MTOK, MAX_BUDGET_USD
from .prompts import build_observe_and_act_prompt, build_reflection_prompt


class ThinkAloudEngine:
    """Manages Claude API calls for think-aloud narration and action decisions."""

    def __init__(self, model: str = DEFAULT_MODEL, budget: float = MAX_BUDGET_USD):
        self.client = anthropic.Anthropic()
        self.model = model
        self.budget = budget
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

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
        """Make a single Claude API call."""
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

    def observe_and_act(
        self,
        persona: dict,
        page_state: str,
        url: str,
        interactive_elements: str,
        action_history: list[str],
        journey_context: str,
    ) -> dict:
        """Generate think-aloud observations and decide next action."""
        prompt = build_observe_and_act_prompt(
            persona, page_state, url, interactive_elements,
            action_history, journey_context,
        )
        raw = self._call(prompt, max_tokens=1200)
        return _parse_json(raw)

    def reflect(self, persona: dict, transcript_summary: str) -> dict:
        """Generate final reflection after assessment completion."""
        prompt = build_reflection_prompt(persona, transcript_summary)
        raw = self._call(prompt, max_tokens=600)
        return _parse_json(raw)

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

"""Session transcript recorder for think-aloud protocol.

v2: Extended schema with fast_reaction, cognitive_walkthrough,
SUS scores, behavioral_events, and protocol version tagging.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import PROTOCOL_VERSION


class SessionRecorder:
    """Accumulates think-aloud data for a single session."""

    def __init__(self, persona: dict, journey: str, output_dir: str):
        self.session_id = str(uuid.uuid4())[:8]
        self.persona = persona
        self.journey = journey
        self.output_dir = Path(output_dir)
        self.pages: list[dict] = []
        self.action_history: list[str] = []
        self.reflection: dict = {}
        self.result: dict = {}
        self.sus: dict = {}
        self.behavioral_events: list[dict] = []
        self.started_at = datetime.now(timezone.utc).isoformat()

    def record_page(
        self,
        url: str,
        llm_response: dict,
        screenshot_path: str = None,
        fast_reaction: dict = None,
        behavioral_events: list[str] = None,
    ):
        """Record a single page observation + action.

        v2 additions: fast_reaction (from observe_fast), behavioral_events
        (hesitations, misclicks, re-reads).
        """
        thoughts = llm_response.get("thoughts", [])
        action = llm_response.get("action", {})
        time_est = llm_response.get("time_estimate", "unknown")

        # Build action description for history
        action_desc = f"{action.get('type', '?')} on {action.get('selector', '?')}"
        if action.get("value"):
            action_desc += f" = {action['value']}"
        self.action_history.append(action_desc)

        page_record = {
            "url": url,
            "thoughts": thoughts,
            "action": action,
            "time_estimate": time_est,
            "screenshot": screenshot_path,
        }

        # v2: Fast reaction and CW data
        if fast_reaction:
            page_record["fast_reaction"] = {
                "first_impression": fast_reaction.get("first_impression"),
                "clarity_score": fast_reaction.get("clarity_score"),
                "emotional_reaction": fast_reaction.get("emotional_reaction"),
                "cognitive_walkthrough": fast_reaction.get("cognitive_walkthrough", {}),
            }
            page_record["hesitation"] = action.get("hesitation", "none")

        # v2: Behavioral events
        if behavioral_events:
            page_record["behavioral_events"] = behavioral_events
            for event in behavioral_events:
                self.behavioral_events.append({
                    "event": event,
                    "url": url,
                })

        self.pages.append(page_record)

    def record_reflection(self, reflection: dict):
        self.reflection = reflection

    def record_result(self, result: dict):
        self.result = result

    def record_sus(self, sus_data: dict):
        """Record SUS questionnaire results."""
        self.sus = sus_data

    def transcript_summary(self) -> str:
        """Build a summary of the session for the reflection prompt."""
        lines = []
        for i, page in enumerate(self.pages):
            url = page["url"].split("/")[-1] or "home"
            lines.append(f"Page {i+1} ({url}):")

            # v2: Include fast reaction if available
            fr = page.get("fast_reaction")
            if fr:
                lines.append(f"  [first impression] {fr.get('first_impression', '?')}")
                lines.append(f"  [clarity] {fr.get('clarity_score', '?')}/5 | "
                             f"feeling: {fr.get('emotional_reaction', '?')}")

            for t in page.get("thoughts", []):
                lines.append(f"  [{t['type']}] {t['thought'][:120]}")
            action = page.get("action", {})
            hesitation = page.get("hesitation", "none")
            lines.append(f"  -> Action: {action.get('type', '?')} {action.get('selector', '')} "
                         f"(hesitation: {hesitation})")

            # v2: Behavioral events
            events = page.get("behavioral_events", [])
            if events:
                lines.append(f"  [behavior] {', '.join(events)}")

        if self.result:
            lines.append(f"\nResult: SAE L{self.result.get('sae_level', '?')}, "
                         f"EPIAS {self.result.get('epias_stage', '?')}")
        return "\n".join(lines)

    def save(self):
        """Write session JSON to output directory."""
        sessions_dir = self.output_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # Build persona data — include v2 fields if available
        persona_data = {
            "archetype": self.persona["archetype_id"],
            "archetype_name": self.persona["archetype_name"],
            "role": self.persona["role"],
            "years": self.persona["years"],
            "industry": self.persona["industry"],
            "age_range": self.persona["age_range"],
            "ai_comfort": self.persona["ai_comfort"],
            "motivation": self.persona["motivation"],
        }
        # v2 persona fields
        if "big5" in self.persona:
            persona_data["big5"] = self.persona["big5"]
        if "tech_beliefs" in self.persona:
            persona_data["tech_beliefs"] = self.persona["tech_beliefs"]
        if "confusion_prob" in self.persona:
            persona_data["confusion_prob"] = self.persona["confusion_prob"]
        if "reading_speed" in self.persona:
            persona_data["reading_speed"] = self.persona["reading_speed"]

        data = {
            "protocol_version": PROTOCOL_VERSION,
            "session_id": self.session_id,
            "persona": persona_data,
            "journey": self.journey,
            "pages": self.pages,
            "reflection": self.reflection,
            "result": self.result,
            "sus": self.sus,
            "behavioral_events_summary": {
                "total": len(self.behavioral_events),
                "events": self.behavioral_events,
            },
            "started_at": self.started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        path = sessions_dir / f"{self.session_id}_{self.persona['archetype_id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(path)

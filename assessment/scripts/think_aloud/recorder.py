"""Session transcript recorder for think-aloud protocol."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


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
        self.started_at = datetime.now(timezone.utc).isoformat()

    def record_page(self, url: str, llm_response: dict, screenshot_path: str = None):
        """Record a single page observation + action."""
        thoughts = llm_response.get("thoughts", [])
        action = llm_response.get("action", {})
        time_est = llm_response.get("time_estimate", "unknown")

        # Build action description for history
        action_desc = f"{action.get('type', '?')} on {action.get('selector', '?')}"
        if action.get("value"):
            action_desc += f" = {action['value']}"
        self.action_history.append(action_desc)

        self.pages.append({
            "url": url,
            "thoughts": thoughts,
            "action": action,
            "time_estimate": time_est,
            "screenshot": screenshot_path,
        })

    def record_reflection(self, reflection: dict):
        self.reflection = reflection

    def record_result(self, result: dict):
        self.result = result

    def transcript_summary(self) -> str:
        """Build a summary of the session for the reflection prompt."""
        lines = []
        for i, page in enumerate(self.pages):
            url = page["url"].split("/")[-1] or "home"
            lines.append(f"Page {i+1} ({url}):")
            for t in page.get("thoughts", []):
                lines.append(f"  [{t['type']}] {t['thought'][:120]}")
            action = page.get("action", {})
            lines.append(f"  -> Action: {action.get('type', '?')} {action.get('selector', '')}")
        if self.result:
            lines.append(f"\nResult: SAE L{self.result.get('sae_level', '?')}, "
                          f"EPIAS {self.result.get('epias_stage', '?')}")
        return "\n".join(lines)

    def save(self):
        """Write session JSON to output directory."""
        sessions_dir = self.output_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": self.session_id,
            "persona": {
                "archetype": self.persona["archetype_id"],
                "archetype_name": self.persona["archetype_name"],
                "role": self.persona["role"],
                "years": self.persona["years"],
                "industry": self.persona["industry"],
                "age_range": self.persona["age_range"],
                "ai_comfort": self.persona["ai_comfort"],
                "motivation": self.persona["motivation"],
            },
            "journey": self.journey,
            "pages": self.pages,
            "reflection": self.reflection,
            "result": self.result,
            "started_at": self.started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        path = sessions_dir / f"{self.session_id}_{self.persona['archetype_id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(path)

"""Post-run analysis of think-aloud session transcripts."""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_sessions(output_dir: str) -> list[dict]:
    """Load all session JSONs from the output directory."""
    sessions_dir = Path(output_dir) / "sessions"
    sessions = []
    for path in sorted(sessions_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            sessions.append(json.load(f))
    return sessions


def analyze(sessions: list[dict]) -> dict:
    """Run all analyses on completed sessions."""
    return {
        "summary": _summary(sessions),
        "usability_issues": _usability_issues(sessions),
        "question_confusion": _question_confusion(sessions),
        "persona_satisfaction": _persona_satisfaction(sessions),
        "flow_completion": _flow_completion(sessions),
        "theme_frequency": _theme_frequency(sessions),
        "self_awareness_highlights": _self_awareness(sessions),
        "emotional_arc": _emotional_arc(sessions),
    }


def _summary(sessions: list[dict]) -> dict:
    archetypes = Counter(s["persona"]["archetype"] for s in sessions)
    nps_scores = [s["reflection"].get("nps_score", 0) for s in sessions if s.get("reflection")]
    return {
        "total_sessions": len(sessions),
        "archetypes": dict(archetypes),
        "avg_nps": round(sum(nps_scores) / max(len(nps_scores), 1), 1),
        "nps_range": [min(nps_scores, default=0), max(nps_scores, default=0)],
        "pages_per_session": round(sum(len(s["pages"]) for s in sessions) / max(len(sessions), 1), 1),
    }


def _usability_issues(sessions: list[dict]) -> list[dict]:
    """Extract and rank usability issues by frequency."""
    issues = []
    for s in sessions:
        # From page-level thoughts
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                if thought.get("type") == "usability" and thought.get("thought"):
                    issues.append({
                        "thought": thought["thought"],
                        "url": page.get("url", ""),
                        "element": thought.get("element"),
                        "archetype": s["persona"]["archetype"],
                    })
        # From reflection
        for issue in s.get("reflection", {}).get("usability_issues", []):
            issues.append({
                "thought": issue,
                "url": "reflection",
                "element": None,
                "archetype": s["persona"]["archetype"],
            })

    # Group by page
    by_page = defaultdict(list)
    for issue in issues:
        page_key = issue["url"].split("/")[-1] or "home"
        by_page[page_key].append(issue["thought"])

    ranked = []
    for page, thoughts in sorted(by_page.items(), key=lambda x: -len(x[1])):
        ranked.append({
            "page": page,
            "count": len(thoughts),
            "examples": thoughts[:5],
        })

    return ranked


def _question_confusion(sessions: list[dict]) -> list[dict]:
    """Identify which questions cause the most hesitation."""
    confusion_signals = defaultdict(list)

    for s in sessions:
        for page in s.get("pages", []):
            url = page.get("url", "")
            if "/assess" not in url:
                continue
            for thought in page.get("thoughts", []):
                text = thought.get("thought", "").lower()
                # Look for confusion signals
                if any(w in text for w in [
                    "confus", "unclear", "not sure", "what does",
                    "hesitat", "between", "hard to", "ambiguous",
                    "don't understand", "which one", "tricky",
                ]):
                    action = page.get("action", {})
                    selector = action.get("selector", "")
                    confusion_signals[selector or url].append({
                        "thought": thought["thought"][:150],
                        "type": thought["type"],
                        "archetype": s["persona"]["archetype"],
                    })

    ranked = []
    for question, signals in sorted(confusion_signals.items(), key=lambda x: -len(x[1])):
        ranked.append({
            "question": question,
            "confusion_count": len(signals),
            "archetypes_affected": list({s["archetype"] for s in signals}),
            "examples": [s["thought"] for s in signals[:3]],
        })

    return ranked[:15]


def _persona_satisfaction(sessions: list[dict]) -> list[dict]:
    """NPS and satisfaction by archetype."""
    by_archetype = defaultdict(list)
    for s in sessions:
        nps = s.get("reflection", {}).get("nps_score")
        if nps is not None:
            by_archetype[s["persona"]["archetype"]].append({
                "nps": nps,
                "would_share": s.get("reflection", {}).get("would_share", False),
                "reason": s.get("reflection", {}).get("nps_reason", ""),
            })

    results = []
    for archetype, data in sorted(by_archetype.items()):
        scores = [d["nps"] for d in data]
        results.append({
            "archetype": archetype,
            "avg_nps": round(sum(scores) / len(scores), 1),
            "min_nps": min(scores),
            "max_nps": max(scores),
            "share_rate": round(sum(1 for d in data if d["would_share"]) / len(data), 2),
            "sample_reasons": [d["reason"] for d in data[:2]],
        })

    return sorted(results, key=lambda x: x["avg_nps"])


def _flow_completion(sessions: list[dict]) -> dict:
    """Track completion rates."""
    completed = sum(1 for s in sessions if s.get("result"))
    with_reflection = sum(1 for s in sessions if s.get("reflection"))
    return {
        "total": len(sessions),
        "completed_assessment": completed,
        "completion_rate": round(completed / max(len(sessions), 1), 2),
        "with_reflection": with_reflection,
    }


def _theme_frequency(sessions: list[dict]) -> dict:
    """Count frequency of thought types across all sessions."""
    counts = Counter()
    for s in sessions:
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                counts[thought.get("type", "unknown")] += 1
    return dict(counts.most_common())


def _self_awareness(sessions: list[dict]) -> list[dict]:
    """Extract notable self-awareness moments."""
    moments = []
    for s in sessions:
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                if thought.get("type") == "self_awareness" and thought.get("thought"):
                    moments.append({
                        "thought": thought["thought"],
                        "archetype": s["persona"]["archetype"],
                        "url": page.get("url", ""),
                    })
    return moments[:20]


def _emotional_arc(sessions: list[dict]) -> list[dict]:
    """Track emotional progression through the assessment."""
    arcs = []
    for s in sessions:
        emotions = []
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                if thought.get("type") == "emotion":
                    emotions.append({
                        "page": page.get("url", "").split("/")[-1] or "home",
                        "emotion": thought["thought"][:100],
                    })
        if emotions:
            arcs.append({
                "archetype": s["persona"]["archetype"],
                "arc": emotions,
            })
    return arcs[:10]


def write_report(analysis: dict, output_dir: str):
    """Write markdown report from analysis results."""
    report_path = Path(output_dir) / "report.md"

    lines = ["# Think-Aloud Protocol Report", ""]
    summary = analysis["summary"]
    lines.append(f"**Sessions:** {summary['total_sessions']} | "
                  f"**Avg NPS:** {summary['avg_nps']} | "
                  f"**Pages/session:** {summary['pages_per_session']}")
    lines.append("")

    # Archetypes
    lines.append("## Persona Coverage")
    for arch, count in sorted(summary["archetypes"].items()):
        lines.append(f"- {arch}: {count} sessions")
    lines.append("")

    # Usability issues
    lines.append("## Usability Issues (by frequency)")
    for issue in analysis["usability_issues"][:10]:
        lines.append(f"\n### {issue['page']} ({issue['count']} mentions)")
        for ex in issue["examples"][:3]:
            lines.append(f"- {ex}")
    lines.append("")

    # Question confusion
    lines.append("## Question Confusion Analysis")
    for q in analysis["question_confusion"][:8]:
        lines.append(f"\n**{q['question']}** ({q['confusion_count']} confusion signals)")
        lines.append(f"  Archetypes affected: {', '.join(q['archetypes_affected'])}")
        for ex in q["examples"]:
            lines.append(f"  - {ex}")
    lines.append("")

    # Persona satisfaction
    lines.append("## Persona Satisfaction (NPS by archetype)")
    lines.append("| Archetype | Avg NPS | Range | Share Rate |")
    lines.append("|-----------|---------|-------|------------|")
    for p in analysis["persona_satisfaction"]:
        lines.append(f"| {p['archetype']} | {p['avg_nps']} | "
                      f"{p['min_nps']}-{p['max_nps']} | {p['share_rate']:.0%} |")
    lines.append("")

    # Flow completion
    fc = analysis["flow_completion"]
    lines.append("## Flow Completion")
    lines.append(f"- Completion rate: {fc['completion_rate']:.0%} "
                  f"({fc['completed_assessment']}/{fc['total']})")
    lines.append("")

    # Self-awareness highlights
    lines.append("## Notable Self-Awareness Moments")
    for m in analysis["self_awareness_highlights"][:10]:
        lines.append(f"- **{m['archetype']}**: {m['thought']}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    # Also save raw analysis JSON
    json_path = Path(output_dir) / "analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    return str(report_path)

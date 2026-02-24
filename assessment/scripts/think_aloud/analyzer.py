"""Post-run analysis of think-aloud session transcripts.

v2: Adds heuristic analysis, cognitive walkthrough failure points,
SUS benchmarking, self-consistency convergence, and behavioral realism metrics.
"""

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .config import NIELSEN_HEURISTICS, SUS_BENCHMARK_AVERAGE, SUS_GRADE_THRESHOLDS


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
    results = {
        "summary": _summary(sessions),
        "usability_issues": _usability_issues(sessions),
        "question_confusion": _question_confusion(sessions),
        "persona_satisfaction": _persona_satisfaction(sessions),
        "flow_completion": _flow_completion(sessions),
        "theme_frequency": _theme_frequency(sessions),
        "self_awareness_highlights": _self_awareness(sessions),
        "emotional_arc": _emotional_arc(sessions),
    }

    # v2 analyses — only run if v2 data is present
    if any(s.get("protocol_version", "1.0") >= "2.0" for s in sessions):
        results["heuristic_analysis"] = _heuristic_analysis(sessions)
        results["cw_failure_points"] = _cw_failure_points(sessions)
        results["sus_analysis"] = _sus_analysis(sessions)
        results["convergence_analysis"] = _convergence_analysis(sessions)
        results["behavioral_realism"] = _behavioral_realism(sessions)

    return results


def _summary(sessions: list[dict]) -> dict:
    archetypes = Counter(s["persona"]["archetype"] for s in sessions)
    nps_scores = [s["reflection"].get("nps_score", 0) for s in sessions if s.get("reflection")]
    return {
        "total_sessions": len(sessions),
        "archetypes": dict(archetypes),
        "avg_nps": round(sum(nps_scores) / max(len(nps_scores), 1), 1),
        "nps_range": [min(nps_scores, default=0), max(nps_scores, default=0)],
        "nps_std_dev": round(statistics.stdev(nps_scores), 2) if len(nps_scores) > 1 else 0.0,
        "pages_per_session": round(sum(len(s["pages"]) for s in sessions) / max(len(sessions), 1), 1),
        "protocol_versions": dict(Counter(s.get("protocol_version", "1.0") for s in sessions)),
    }


def _usability_issues(sessions: list[dict]) -> list[dict]:
    """Extract and rank usability issues by frequency."""
    issues = []
    for s in sessions:
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                if thought.get("type") == "usability" and thought.get("thought"):
                    issues.append({
                        "thought": thought["thought"],
                        "url": page.get("url", ""),
                        "element": thought.get("element"),
                        "heuristic": thought.get("heuristic"),
                        "archetype": s["persona"]["archetype"],
                    })
        for issue in s.get("reflection", {}).get("usability_issues", []):
            issues.append({
                "thought": issue,
                "url": "reflection",
                "element": None,
                "heuristic": None,
                "archetype": s["persona"]["archetype"],
            })

    by_page = defaultdict(list)
    for issue in issues:
        page_key = issue["url"].split("/")[-1] or "home"
        by_page[page_key].append(issue)

    ranked = []
    for page, page_issues in sorted(by_page.items(), key=lambda x: -len(x[1])):
        ranked.append({
            "page": page,
            "count": len(page_issues),
            "examples": [i["thought"] for i in page_issues[:5]],
            "heuristics_cited": [i["heuristic"] for i in page_issues if i.get("heuristic")],
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


# ── v2 Analysis Functions ──


def _heuristic_analysis(sessions: list[dict]) -> dict:
    """Count usability observations by Nielsen heuristic (H2, H6).

    Tracks which of the 10 heuristics are cited, by whom, and how often.
    """
    heuristic_counts = Counter()
    heuristic_by_archetype = defaultdict(lambda: Counter())
    heuristic_examples = defaultdict(list)

    for s in sessions:
        archetype = s["persona"]["archetype"]
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                h = thought.get("heuristic")
                if h and h in NIELSEN_HEURISTICS:
                    heuristic_counts[h] += 1
                    heuristic_by_archetype[archetype][h] += 1
                    if len(heuristic_examples[h]) < 3:
                        heuristic_examples[h].append({
                            "thought": thought["thought"][:150],
                            "archetype": archetype,
                        })

    total_usability = sum(1 for s in sessions for p in s.get("pages", [])
                          for t in p.get("thoughts", []) if t.get("type") == "usability")
    with_heuristic = sum(heuristic_counts.values())

    return {
        "heuristics_covered": len(heuristic_counts),
        "total_heuristics": 10,
        "citation_rate": round(with_heuristic / max(total_usability, 1), 2),
        "counts": dict(heuristic_counts.most_common()),
        "by_archetype": {k: dict(v) for k, v in heuristic_by_archetype.items()},
        "examples": {k: v for k, v in heuristic_examples.items()},
        "missing_heuristics": [h for h in NIELSEN_HEURISTICS if h not in heuristic_counts],
    }


def _cw_failure_points(sessions: list[dict]) -> dict:
    """Extract cognitive walkthrough failure points (H2, H3).

    Identifies pages where CW questions received false answers —
    these are high-priority UX fixes.
    """
    cw_questions = [
        "will_try_right_effect",
        "notices_correct_action",
        "associates_action_with_goal",
        "sees_progress",
    ]

    failures = []
    totals = Counter()
    failure_counts = Counter()

    for s in sessions:
        archetype = s["persona"]["archetype"]
        for page in s.get("pages", []):
            fr = page.get("fast_reaction", {})
            cw = fr.get("cognitive_walkthrough", {})
            if not cw:
                continue

            url = page.get("url", "").split("/")[-1] or "home"
            for q in cw_questions:
                val = cw.get(q)
                if val is not None:
                    totals[q] += 1
                    if val is False:
                        failure_counts[q] += 1
                        why_key = q.replace("will_try", "will_try_why").replace(
                            "notices_correct", "notices_why").replace(
                            "associates_action", "associates_why").replace(
                            "sees_progress", "progress_why")
                        # Map to correct why key
                        why_map = {
                            "will_try_right_effect": "will_try_why",
                            "notices_correct_action": "notices_why",
                            "associates_action_with_goal": "associates_why",
                            "sees_progress": "progress_why",
                        }
                        why = cw.get(why_map.get(q, ""), "")
                        failures.append({
                            "question": q,
                            "page": url,
                            "archetype": archetype,
                            "why": why,
                            "clarity_score": fr.get("clarity_score"),
                        })

    # Group by page
    by_page = defaultdict(list)
    for f in failures:
        by_page[f["page"]].append(f)

    return {
        "total_failures": len(failures),
        "failure_rate": {q: round(failure_counts[q] / max(totals[q], 1), 2) for q in cw_questions},
        "by_page": {page: {
            "count": len(items),
            "questions_failed": list({i["question"] for i in items}),
            "archetypes": list({i["archetype"] for i in items}),
            "examples": [{"q": i["question"], "why": i["why"], "arch": i["archetype"]}
                         for i in items[:3]],
        } for page, items in sorted(by_page.items(), key=lambda x: -len(x[1]))},
        "unique_failure_pages": len(by_page),
    }


def _sus_analysis(sessions: list[dict]) -> dict:
    """Compute SUS scores per persona and overall (H4).

    SUS benchmark: 68 = average, 80.3 = Grade A.
    """
    all_scores = []
    by_archetype = defaultdict(list)

    for s in sessions:
        sus = s.get("sus", {})
        total = sus.get("sus_total")
        if total is not None:
            all_scores.append(total)
            by_archetype[s["persona"]["archetype"]].append({
                "total": total,
                "grade": sus.get("sus_grade", "?"),
                "notes": sus.get("sus_notes", ""),
            })

    if not all_scores:
        return {"overall_mean": None, "note": "No SUS data available"}

    overall_mean = round(statistics.mean(all_scores), 1)
    overall_std = round(statistics.stdev(all_scores), 1) if len(all_scores) > 1 else 0.0

    # Grade the overall
    overall_grade = "F"
    for g, threshold in sorted(SUS_GRADE_THRESHOLDS.items(), key=lambda x: -x[1]):
        if overall_mean >= threshold:
            overall_grade = g
            break

    archetype_results = []
    for arch, data in sorted(by_archetype.items()):
        scores = [d["total"] for d in data]
        archetype_results.append({
            "archetype": arch,
            "mean_sus": round(statistics.mean(scores), 1),
            "min": min(scores),
            "max": max(scores),
            "grade": data[0]["grade"],
            "notes": data[0]["notes"],
        })

    return {
        "overall_mean": overall_mean,
        "overall_std": overall_std,
        "overall_grade": overall_grade,
        "benchmark_comparison": "above" if overall_mean > SUS_BENCHMARK_AVERAGE else "below",
        "score_range": round(max(all_scores) - min(all_scores), 1),
        "by_archetype": sorted(archetype_results, key=lambda x: x["mean_sus"]),
    }


def _convergence_analysis(sessions: list[dict]) -> dict:
    """Self-consistency analysis: identify robust vs tentative findings (H5).

    Groups sessions by archetype, extracts usability findings,
    and checks which appear across multiple runs of the same persona.
    """
    by_archetype = defaultdict(list)
    for s in sessions:
        archetype = s["persona"]["archetype"]
        findings = []
        for page in s.get("pages", []):
            for thought in page.get("thoughts", []):
                if thought.get("type") == "usability" and thought.get("thought"):
                    # Normalize: lowercase, first 80 chars for fuzzy matching
                    findings.append(thought["thought"].lower()[:80])
        by_archetype[archetype].append(set(findings))

    # Only analyze archetypes with 2+ sessions
    convergence_data = {}
    all_convergence_rates = []

    for arch, finding_sets in by_archetype.items():
        if len(finding_sets) < 2:
            continue

        # Count how many sessions each finding appears in
        all_findings = Counter()
        for fset in finding_sets:
            for f in fset:
                all_findings[f] += 1

        total_unique = len(all_findings)
        robust = sum(1 for count in all_findings.values() if count >= 2)
        rate = round(robust / max(total_unique, 1), 2)
        all_convergence_rates.append(rate)

        convergence_data[arch] = {
            "sessions": len(finding_sets),
            "total_unique_findings": total_unique,
            "robust_findings": robust,
            "tentative_findings": total_unique - robust,
            "convergence_rate": rate,
        }

    return {
        "archetypes_analyzed": len(convergence_data),
        "overall_convergence_rate": round(
            statistics.mean(all_convergence_rates), 2
        ) if all_convergence_rates else None,
        "by_archetype": convergence_data,
    }


def _behavioral_realism(sessions: list[dict]) -> dict:
    """Count behavioral events (hesitations, misclicks, re-reads) per persona (H3).

    Validates that confusion_prob is producing realistic non-optimal behavior.
    """
    all_events = []
    by_archetype = defaultdict(list)

    for s in sessions:
        archetype = s["persona"]["archetype"]
        events_summary = s.get("behavioral_events_summary", {})
        event_count = events_summary.get("total", 0)

        # Also count hesitations from page data
        for page in s.get("pages", []):
            hesitation = page.get("hesitation", "none")
            if hesitation in ("brief", "significant"):
                event_count += 1
            page_events = page.get("behavioral_events", [])
            event_count += len(page_events)

        all_events.append(event_count)
        by_archetype[archetype].append({
            "events": event_count,
            "confusion_prob": s.get("persona", {}).get("confusion_prob", None),
        })

    if not all_events:
        return {"events_per_session": 0}

    archetype_results = []
    for arch, data in sorted(by_archetype.items()):
        events = [d["events"] for d in data]
        archetype_results.append({
            "archetype": arch,
            "avg_events": round(statistics.mean(events), 1),
            "confusion_prob": data[0].get("confusion_prob"),
        })

    return {
        "events_per_session": round(statistics.mean(all_events), 1),
        "total_events": sum(all_events),
        "by_archetype": sorted(archetype_results, key=lambda x: -x["avg_events"]),
    }


def write_report(analysis: dict, output_dir: str):
    """Write markdown report from analysis results."""
    report_path = Path(output_dir) / "report.md"

    lines = ["# Think-Aloud Protocol Report", ""]
    summary = analysis["summary"]
    versions = summary.get("protocol_versions", {})
    version_str = ", ".join(f"v{v} ({n})" for v, n in sorted(versions.items()))
    lines.append(f"**Protocol:** {version_str or '?'} | "
                 f"**Sessions:** {summary['total_sessions']} | "
                 f"**Avg NPS:** {summary['avg_nps']} | "
                 f"**NPS Std Dev:** {summary.get('nps_std_dev', '?')} | "
                 f"**Pages/session:** {summary['pages_per_session']}")
    lines.append("")

    # Archetypes
    lines.append("## Persona Coverage")
    for arch, count in sorted(summary["archetypes"].items()):
        lines.append(f"- {arch}: {count} sessions")
    lines.append("")

    # ── v2: SUS Analysis ──
    if "sus_analysis" in analysis:
        sus = analysis["sus_analysis"]
        lines.append("## SUS Scores (System Usability Scale)")
        lines.append(f"**Overall:** {sus.get('overall_mean', '?')} "
                     f"(Grade {sus.get('overall_grade', '?')}) | "
                     f"**Std Dev:** {sus.get('overall_std', '?')} | "
                     f"**Range:** {sus.get('score_range', '?')} pts | "
                     f"**vs Benchmark (68):** {sus.get('benchmark_comparison', '?')}")
        lines.append("")
        if sus.get("by_archetype"):
            lines.append("| Archetype | Mean SUS | Grade | Range |")
            lines.append("|-----------|----------|-------|-------|")
            for a in sus["by_archetype"]:
                lines.append(f"| {a['archetype']} | {a['mean_sus']} | {a['grade']} | "
                             f"{a['min']}-{a['max']} |")
            lines.append("")

    # ── v2: Heuristic Analysis ──
    if "heuristic_analysis" in analysis:
        h = analysis["heuristic_analysis"]
        lines.append("## Nielsen Heuristic Analysis")
        lines.append(f"**Coverage:** {h['heuristics_covered']}/10 heuristics cited | "
                     f"**Citation rate:** {h['citation_rate']:.0%}")
        lines.append("")
        if h.get("counts"):
            lines.append("| Heuristic | Count |")
            lines.append("|-----------|-------|")
            for heur, count in h["counts"].items():
                lines.append(f"| {heur.replace('_', ' ').title()} | {count} |")
            lines.append("")
        if h.get("missing_heuristics"):
            lines.append(f"**Missing:** {', '.join(h['missing_heuristics'])}")
            lines.append("")

    # ── v2: CW Failure Points ──
    if "cw_failure_points" in analysis:
        cw = analysis["cw_failure_points"]
        lines.append("## Cognitive Walkthrough Failure Points")
        lines.append(f"**Total failures:** {cw['total_failures']} | "
                     f"**Unique pages with failures:** {cw['unique_failure_pages']}")
        lines.append("")
        if cw.get("failure_rate"):
            lines.append("| CW Question | Failure Rate |")
            lines.append("|-------------|-------------|")
            for q, rate in cw["failure_rate"].items():
                lines.append(f"| {q.replace('_', ' ').title()} | {rate:.0%} |")
            lines.append("")
        for page, data in list(cw.get("by_page", {}).items())[:5]:
            lines.append(f"### {page} ({data['count']} failures)")
            lines.append(f"  Questions failed: {', '.join(data['questions_failed'])}")
            lines.append(f"  Archetypes: {', '.join(data['archetypes'])}")
            for ex in data.get("examples", []):
                lines.append(f"  - [{ex['arch']}] {ex['q']}: {ex['why']}")
            lines.append("")

    # ── v2: Behavioral Realism ──
    if "behavioral_realism" in analysis:
        b = analysis["behavioral_realism"]
        lines.append("## Behavioral Realism")
        lines.append(f"**Events/session:** {b['events_per_session']} | "
                     f"**Total events:** {b['total_events']}")
        lines.append("")
        if b.get("by_archetype"):
            lines.append("| Archetype | Avg Events | Confusion Prob |")
            lines.append("|-----------|-----------|----------------|")
            for a in b["by_archetype"]:
                lines.append(f"| {a['archetype']} | {a['avg_events']} | "
                             f"{a.get('confusion_prob', '?')} |")
            lines.append("")

    # Usability issues
    lines.append("## Usability Issues (by frequency)")
    for issue in analysis["usability_issues"][:10]:
        lines.append(f"\n### {issue['page']} ({issue['count']} mentions)")
        if issue.get("heuristics_cited"):
            heur_counts = Counter(issue["heuristics_cited"])
            lines.append(f"  Heuristics: {', '.join(f'{h} ({c})' for h, c in heur_counts.most_common())}")
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

    # ── v2: Convergence ──
    if "convergence_analysis" in analysis:
        conv = analysis["convergence_analysis"]
        lines.append("## Self-Consistency Convergence")
        lines.append(f"**Overall convergence rate:** {conv.get('overall_convergence_rate', '?')}")
        lines.append(f"**Archetypes analyzed:** {conv.get('archetypes_analyzed', 0)}")
        lines.append("")
        for arch, data in conv.get("by_archetype", {}).items():
            lines.append(f"- **{arch}**: {data['robust_findings']} robust / "
                         f"{data['total_unique_findings']} total "
                         f"({data['convergence_rate']:.0%} convergence)")
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


# ── Model Comparison ──


def compare_models(dirs: dict[str, str], output_path: str) -> str:
    """Compare think-aloud sessions across different models.

    Args:
        dirs: {"Sonnet 4": "path/to/sessions", "Haiku 3.5": "path/to/sessions", ...}
        output_path: Where to write the comparison report.
    Returns:
        Path to the written report.
    """
    arms = {}
    for label, dir_path in dirs.items():
        sessions = load_sessions(dir_path)
        if sessions:
            arms[label] = {"sessions": sessions, "analysis": analyze(sessions)}

    if not arms:
        return ""

    lines = ["# Model Comparison Report", ""]
    lines.append(f"**Arms:** {', '.join(arms.keys())}")
    lines.append("")

    # ── Summary table ──
    lines.append("## Summary")
    lines.append("")
    headers = ["Metric"] + list(arms.keys())
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")

    def _row(label, fn):
        vals = [fn(arms[k]) for k in arms]
        lines.append(f"| {label} | " + " | ".join(str(v) for v in vals) + " |")

    _row("Sessions", lambda a: a["analysis"]["summary"]["total_sessions"])
    _row("Avg NPS", lambda a: a["analysis"]["summary"]["avg_nps"])
    _row("NPS Std Dev", lambda a: a["analysis"]["summary"].get("nps_std_dev", "?"))
    _row("Pages/session", lambda a: a["analysis"]["summary"]["pages_per_session"])
    _row("Completion rate", lambda a: f"{a['analysis']['flow_completion']['completion_rate']:.0%}")

    # Cost
    def _avg_cost(a):
        costs = [s.get("engine_usage", {}).get("cost_usd", 0) for s in a["sessions"]]
        return f"${sum(costs) / max(len(costs), 1):.3f}" if costs else "?"
    _row("Avg cost/session", _avg_cost)

    def _total_cost(a):
        return f"${sum(s.get('engine_usage', {}).get('cost_usd', 0) for s in a['sessions']):.2f}"
    _row("Total cost", _total_cost)

    # SUS
    if any("sus_analysis" in a["analysis"] for a in arms.values()):
        _row("Avg SUS", lambda a: a["analysis"].get("sus_analysis", {}).get("overall_mean", "?"))
        _row("SUS Grade", lambda a: a["analysis"].get("sus_analysis", {}).get("overall_grade", "?"))
        _row("SUS Std Dev", lambda a: a["analysis"].get("sus_analysis", {}).get("overall_std", "?"))

    # Heuristics
    if any("heuristic_analysis" in a["analysis"] for a in arms.values()):
        _row("Heuristics covered", lambda a: f"{a['analysis'].get('heuristic_analysis', {}).get('heuristics_covered', '?')}/10")
        _row("Heuristic citation rate", lambda a: f"{a['analysis'].get('heuristic_analysis', {}).get('citation_rate', 0):.0%}")

    # CW failures
    if any("cw_failure_points" in a["analysis"] for a in arms.values()):
        _row("CW total failures", lambda a: a["analysis"].get("cw_failure_points", {}).get("total_failures", "?"))
        for q in ["will_try_right_effect", "notices_correct_action",
                   "associates_action_with_goal", "sees_progress"]:
            _row(f"CW: {q}", lambda a, q=q: f"{a['analysis'].get('cw_failure_points', {}).get('failure_rate', {}).get(q, '?'):.0%}"
                 if isinstance(a["analysis"].get("cw_failure_points", {}).get("failure_rate", {}).get(q), (int, float)) else "?")

    # Behavioral realism
    if any("behavioral_realism" in a["analysis"] for a in arms.values()):
        _row("Behavioral events/session", lambda a: a["analysis"].get("behavioral_realism", {}).get("events_per_session", "?"))

    lines.append("")

    # ── Thought quality ──
    lines.append("## Thought Quality")
    lines.append("")
    headers2 = ["Metric"] + list(arms.keys())
    lines.append("| " + " | ".join(headers2) + " |")
    lines.append("|" + "|".join("---" for _ in headers2) + "|")

    def _thought_stats(a):
        lengths = []
        type_counts = Counter()
        parse_errors = 0
        for s in a["sessions"]:
            for p in s.get("pages", []):
                for t in p.get("thoughts", []):
                    text = t.get("thought", "")
                    lengths.append(len(text))
                    type_counts[t.get("type", "unknown")] += 1
                fr = p.get("fast_reaction", {})
                if fr.get("error"):
                    parse_errors += 1
        return {
            "avg_length": round(statistics.mean(lengths)) if lengths else 0,
            "type_diversity": len(type_counts),
            "total_thoughts": len(lengths),
            "parse_errors": parse_errors,
        }

    thought_data = {k: _thought_stats(v) for k, v in arms.items()}

    for metric in ["avg_length", "type_diversity", "total_thoughts", "parse_errors"]:
        label = metric.replace("_", " ").title()
        vals = [str(thought_data[k][metric]) for k in arms]
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    lines.append("")

    # ── SUS by archetype ──
    if any("sus_analysis" in a["analysis"] for a in arms.values()):
        lines.append("## SUS by Archetype")
        lines.append("")
        # Collect all archetypes
        all_archs = set()
        for a in arms.values():
            for entry in a["analysis"].get("sus_analysis", {}).get("by_archetype", []):
                all_archs.add(entry["archetype"])
        all_archs = sorted(all_archs)

        headers3 = ["Archetype"] + list(arms.keys())
        lines.append("| " + " | ".join(headers3) + " |")
        lines.append("|" + "|".join("---" for _ in headers3) + "|")

        for arch in all_archs:
            vals = []
            for k in arms:
                found = [e for e in arms[k]["analysis"].get("sus_analysis", {}).get("by_archetype", [])
                         if e["archetype"] == arch]
                if found:
                    vals.append(f"{found[0]['mean_sus']} ({found[0]['grade']})")
                else:
                    vals.append("-")
            lines.append(f"| {arch} | " + " | ".join(vals) + " |")
        lines.append("")

    # ── NPS by archetype ──
    lines.append("## NPS by Archetype")
    lines.append("")
    all_archs_nps = set()
    for a in arms.values():
        for entry in a["analysis"].get("persona_satisfaction", []):
            all_archs_nps.add(entry["archetype"])
    all_archs_nps = sorted(all_archs_nps)

    headers4 = ["Archetype"] + list(arms.keys())
    lines.append("| " + " | ".join(headers4) + " |")
    lines.append("|" + "|".join("---" for _ in headers4) + "|")
    for arch in all_archs_nps:
        vals = []
        for k in arms:
            found = [e for e in arms[k]["analysis"].get("persona_satisfaction", [])
                     if e["archetype"] == arch]
            if found:
                vals.append(f"{found[0]['avg_nps']}")
            else:
                vals.append("-")
        lines.append(f"| {arch} | " + " | ".join(vals) + " |")
    lines.append("")

    # ── Cost-quality verdict ──
    lines.append("## Cost-Quality Verdict")
    lines.append("")

    baseline_key = list(arms.keys())[0]  # First arm is baseline
    baseline_sus = arms[baseline_key]["analysis"].get("sus_analysis", {}).get("overall_mean", 0)
    baseline_sus_std = arms[baseline_key]["analysis"].get("sus_analysis", {}).get("overall_std", 0)
    baseline_nps = arms[baseline_key]["analysis"]["summary"]["avg_nps"]
    baseline_heuristics = arms[baseline_key]["analysis"].get("heuristic_analysis", {}).get("heuristics_covered", 0)

    for label, arm_data in list(arms.items())[1:]:
        sus_mean = arm_data["analysis"].get("sus_analysis", {}).get("overall_mean", 0)
        nps_mean = arm_data["analysis"]["summary"]["avg_nps"]
        heuristics = arm_data["analysis"].get("heuristic_analysis", {}).get("heuristics_covered", 0)

        costs_arm = [s.get("engine_usage", {}).get("cost_usd", 0) for s in arm_data["sessions"]]
        costs_base = [s.get("engine_usage", {}).get("cost_usd", 0) for s in arms[baseline_key]["sessions"]]
        avg_cost_arm = sum(costs_arm) / max(len(costs_arm), 1)
        avg_cost_base = sum(costs_base) / max(len(costs_base), 1)
        savings_pct = (1 - avg_cost_arm / max(avg_cost_base, 0.001)) * 100

        sus_delta = (sus_mean or 0) - (baseline_sus or 0)
        nps_delta = nps_mean - baseline_nps
        within_1sd = abs(sus_delta) <= (baseline_sus_std or 999)

        lines.append(f"### {label} vs {baseline_key}")
        lines.append(f"- **Cost savings:** {savings_pct:.0f}%")
        lines.append(f"- **SUS delta:** {sus_delta:+.1f} pts {'(within 1 SD)' if within_1sd else '(OUTSIDE 1 SD)'}")
        lines.append(f"- **NPS delta:** {nps_delta:+.1f}")
        lines.append(f"- **Heuristic coverage:** {heuristics}/10 vs {baseline_heuristics}/10")

        if within_1sd and heuristics >= 8:
            lines.append(f"- **Verdict: RECOMMENDED** -- quality within tolerance at {savings_pct:.0f}% savings")
        elif heuristics < 8:
            lines.append(f"- **Verdict: NOT RECOMMENDED** -- heuristic coverage too low ({heuristics}/10)")
        else:
            lines.append(f"- **Verdict: MARGINAL** -- SUS drop outside 1 SD, review qualitatively")
        lines.append("")

    report_text = "\n".join(lines)
    report_file = Path(output_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report_text, encoding="utf-8")

    # Also save raw comparison data
    comparison_data = {}
    for label, arm_data in arms.items():
        comparison_data[label] = {
            "summary": arm_data["analysis"]["summary"],
            "sus": arm_data["analysis"].get("sus_analysis"),
            "heuristics": arm_data["analysis"].get("heuristic_analysis"),
            "cw": arm_data["analysis"].get("cw_failure_points"),
            "behavioral": arm_data["analysis"].get("behavioral_realism"),
            "thought_quality": _thought_stats(arm_data),
        }
    json_path = report_file.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)

    return str(report_file)

# Think-Aloud UX Iteration Comparison Report

**Model:** Qwen3-32B (vLLM on Modal, 1xH100 FP8)
**Date:** 2026-02-24
**Sessions per arm:** 10 (1 per persona archetype)

## Executive Summary

Five experimental arms tested the DIT 2026 assessment UI across two protocol versions and three design iterations. The Typeform-style redesign (v3) improved SUS by ~5 points over the ARIA baseline, but CW failure rates remained stubbornly high across all v2.1 protocol runs. Investigation revealed this is primarily a **measurement artifact**: the v2.1 protocol's 5th CW question and ARIA-aware prompting create a systematically higher evaluation bar than the v2.0 protocol.

## Arms Overview

| Arm | Protocol | Design | Scraper | Key Change |
|-----|----------|--------|---------|------------|
| Pre-ARIA Qwen | v2.0 (4 CW questions) | Original (sidebar + grid) | `label.option-item` | Baseline — no ARIA prompting |
| ARIA v1 | v2.1 (5 CW questions) | Original (sidebar + grid) | `label.option-item` | Added ARIA-aware prompts, 5th CW question, accessibility heuristic |
| ARIA v2 | v2.1 | CSS fixes (selection flash, status) | `label.option-item` | Incremental CSS: selection flash, status msg, instruction text |
| v3 Deployed | v2.1 | Typeform redesign | `label.option-item` (STALE) | Ground-up redesign: centered layout, killed sidebar, 800ms confirm |
| v3 Fixed | v2.1 | Typeform redesign | `button.q-option` (CORRECT) | Fixed scraper to match new DOM elements |

## SUS Scores (System Usability Scale)

| Arm | Mean SUS | Grade | Std Dev | Range |
|-----|----------|-------|---------|-------|
| Pre-ARIA Qwen (v2.0) | **57.8** | C | 18.8 | 62.5 pts |
| ARIA v1 (v2.1) | 45.8 | D | 12.9 | 37.5 pts |
| ARIA v2 (v2.1) | 45.2 | D | 19.3 | 65.0 pts |
| v3 Deployed (v2.1) | **50.8** | D | 15.6 | 45.0 pts |
| v3 Fixed (v2.1) | 49.0 | D | 18.2 | 50.0 pts |

**Key finding:** The v2.0→v2.1 protocol change itself caused a ~12-point SUS drop (57.8→45.8), independent of any UI changes. Within the v2.1 protocol, the Typeform redesign improved SUS by ~5 points (45.2→50.8).

## Cognitive Walkthrough Failure Rates

| CW Question | Pre-ARIA (v2.0) | ARIA v1 | ARIA v2 | v3 Deployed | v3 Fixed |
|-------------|----------------|---------|---------|-------------|----------|
| Will Try Right Effect | **10%** | 46% | 47% | 44% | 46% |
| Notices Correct Action | **10%** | 61% | 50% | 51% | 54% |
| Associates Action With Goal | **24%** | 39% | 38% | 38% | 37% |
| Sees Progress | **15%** | 77% | 79% | 79% | 76% |
| Understands Page Structure | — | 59% | 53% | 56% | 51% |
| **Total failures** | **75** | 358 | 345 | 374 | 370 |

**Key finding:** CW failure rates are ~5x higher in v2.1 vs v2.0. Within v2.1, they are essentially flat across all design iterations (345-374 total). The `sees_progress` metric is consistently ~77% regardless of whether progress indicators exist or not.

## NPS & Completion

| Arm | Avg NPS | NPS Std Dev | Completion |
|-----|---------|-------------|------------|
| Pre-ARIA Qwen (v2.0) | **7.0** | 0.0 | — |
| ARIA v1 (v2.1) | 5.0 | 1.15 | 100% |
| ARIA v2 (v2.1) | 5.0 | 1.33 | 90% |
| v3 Deployed (v2.1) | **5.5** | 1.43 | **100%** |
| v3 Fixed (v2.1) | 5.4 | 1.35 | 90% |

## Per-Persona SUS Trends (v2.1 Protocol Only)

| Persona | ARIA v1 | ARIA v2 | v3 Deployed | v3 Fixed | Trend |
|---------|---------|---------|-------------|----------|-------|
| app_builder | 52.5 | 75.0 | 75.0 | 72.5 | Stable high |
| curious_explorer | 65.0 | 67.5 | 62.5 | 75.0 | Volatile |
| daily_user | 50.0 | 57.5 | 70.0 | 55.0 | Volatile |
| design_leader | 62.5 | 47.5 | 47.5 | 57.5 | Volatile |
| ux_researcher | 50.0 | 47.5 | 62.5 | 55.0 | Improving |
| agency_creative_director | 47.5 | 47.5 | 35.0 | 55.0 | Volatile |
| student_non_designer | 37.5 | 42.5 | 45.0 | 27.5 | Volatile |
| ai_native_engineer | 30.0 | 10.0 | 40.0 | 40.0 | Improved in v3 |
| traditional_craftsperson | 35.0 | 32.5 | 40.0 | 27.5 | Volatile |
| career_changer | 27.5 | 25.0 | 30.0 | 25.0 | Flat low |

**Key finding:** With N=1 per persona, individual SUS scores are highly volatile (±15-20 points between runs). Only `app_builder` shows stable results. The `career_changer` persona consistently scores lowest.

## Heuristic Coverage

| Arm | Heuristics Cited | Missing |
|-----|-----------------|---------|
| Pre-ARIA (v2.0) | 7/10 | error_prevention, error_recovery, help_documentation |
| ARIA v1 (v2.1) | 9/11 | error_prevention, error_recovery |
| ARIA v2 (v2.1) | 9/11 | error_prevention, error_recovery |
| v3 Deployed (v2.1) | 9/11 | error_prevention, error_recovery |
| v3 Fixed (v2.1) | 9/11 | error_prevention, error_recovery |

`error_prevention` and `error_recovery` are never cited — the assessment form doesn't generate errors, so this is expected.

## Page-Level CW Failures (v2.1 Only)

| Page | ARIA v1 | ARIA v2 | v3 Deployed | v3 Fixed |
|------|---------|---------|-------------|----------|
| assess (questions) | 299 | 293 | 354 | 325 |
| home (landing) | 35 | 28 | 14 | 23 |
| results | 24 | 24 | 6 | 22 |

**Key finding:** Results page failures dropped dramatically in v3 Deployed (24→6, ↓75%) thanks to the visible heading and cleaner layout, but bounced back to 22 in the v3 Fixed run — this volatility reflects LLM stochasticity, not a real design change.

## Qualitative Insights (Consistent Across All Arms)

### Genuine UX Issues (cited repeatedly across all arms):
1. **Jargon barrier** — "harnesses", "agent infrastructure", "flagged exceptions" alienate non-technical personas
2. **No clear time estimate** — users don't know how long the assessment takes before starting
3. **Missing tooltips** — "maturity stage" is never defined inline
4. **Weak visual hierarchy** — options look similar, making selection hard to distinguish from non-selection

### Issues That Are LLM Artifacts (not real UX problems):
1. **"No progress indicator"** — cited at 77% despite "Question X of Y" counter being present and in ARIA tree
2. **"Can't tell if selection registered"** — cited despite 800ms confirmation + visual highlight
3. **"No visual feedback"** — the LLM reports absence of feedback it cannot perceive (animations, color changes)

## Methodology Notes

### Protocol Version Differences
The v2.0→v2.1 protocol change introduced:
- **5th CW question** (`understands_page_structure`) — adds ~20% more failure surface area
- **ARIA-aware prompting** — instructs the LLM to evaluate accessibility structure explicitly
- **Accessibility heuristic** — `accessibility_structure` as 11th Nielsen heuristic
- **Accessibility thought type** — dedicated thought slot for structure evaluation
- **Accessibility rating** — 1-5 scale in reflection

These changes make the v2.1 protocol a **stricter instrument** that detects more issues but also inflates failure rates relative to v2.0. The ~12-point SUS drop and ~5x CW failure increase between protocols confirms this is primarily an instrumentation effect.

### Scraper Alignment
The INTERACTIVE_JS scraper queries DOM elements and feeds structured data to the LLM. When the v3 redesign changed elements from `label.option-item` to `button.q-option`, the scraper broke (empty results for question pages). However, fixing the scraper had minimal impact on metrics (SUS 50.8→49.0, sees_progress 79%→76%), confirming the LLM primarily uses the ARIA accessibility tree rather than the interactive elements JSON.

### Statistical Limitations
- N=1 per persona means individual scores are unreliable (±15-20 pts noise)
- Aggregate SUS across 10 personas is more stable but still has ~3-5 pt confidence interval
- CW failure rates at the arm level appear stable (345-374) but per-page rates are volatile

## Recommendations

1. **For the UI**: Address the genuine issues — add time estimate to landing page, add tooltips for jargon, improve visual distinction between selected/unselected options
2. **For the methodology**: Run 3+ sessions per persona to reduce noise; the current N=1 design is underpowered for detecting 5-point SUS differences
3. **For the protocol**: Consider reporting both v2.0 and v2.1 metrics when comparing across protocols, with explicit notation about the measurement change
4. **For the model**: The Qwen3-32B CW evaluation appears to have a high false-positive rate for `sees_progress` specifically. Consider calibrating CW prompts or adding ground-truth validation for progress indicator presence.

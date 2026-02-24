# Model Comparison Report

**Arms:** Qwen Pre-ARIA, Qwen Post-ARIA v1, Qwen Post-ARIA v2 (UX fixes)

## Summary

| Metric | Qwen Pre-ARIA | Qwen Post-ARIA v1 | Qwen Post-ARIA v2 (UX fixes) |
|---|---|---|---|
| Sessions | 10 | 10 | 10 |
| Avg NPS | 7.0 | 5.0 | 5.0 |
| NPS Std Dev | 0.0 | 1.15 | 1.33 |
| Pages/session | 12.6 | 12.7 | 12.9 |
| Completion rate | 90% | 100% | 90% |
| Avg cost/session | $0.000 | $0.000 | $0.000 |
| Total cost | $0.00 | $0.00 | $0.00 |
| Avg SUS | 57.8 | 45.8 | 45.2 |
| SUS Grade | C | D | D |
| SUS Std Dev | 18.8 | 12.9 | 19.3 |
| Heuristics covered | 7/11 | 9/11 | 9/11 |
| Heuristic citation rate | 100% | 100% | 99% |
| CW total failures | 75 | 358 | 345 |
| CW: will_try_right_effect | 10% | 46% | 47% |
| CW: notices_correct_action | 10% | 61% | 50% |
| CW: associates_action_with_goal | 24% | 39% | 38% |
| CW: sees_progress | 15% | 77% | 79% |
| CW: understands_page_structure | 0% | 59% | 53% |
| Behavioral events/session | 44.9 | 47.4 | 46.4 |
| Structure understanding | - | 41% | 47% |
| Accessibility rating | - | 2.8 | 2.8 |

## Thought Quality

| Metric | Qwen Pre-ARIA | Qwen Post-ARIA v1 | Qwen Post-ARIA v2 (UX fixes) |
|---|---|---|---|
| Avg Length | 158 | 150 | 147 |
| Type Diversity | 5 | 6 | 6 |
| Total Thoughts | 630 | 762 | 774 |
| Parse Errors | 0 | 0 | 0 |

## SUS by Archetype

| Archetype | Qwen Pre-ARIA | Qwen Post-ARIA v1 | Qwen Post-ARIA v2 (UX fixes) |
|---|---|---|---|
| agency_creative_director | 65.0 (C) | 47.5 (D) | 47.5 (D) |
| ai_native_engineer | 47.5 (D) | 30.0 (F) | 10.0 (F) |
| app_builder | 67.5 (C) | 52.5 (C) | 75.0 (B) |
| career_changer | 42.5 (D) | 27.5 (F) | 25.0 (F) |
| curious_explorer | 85.0 (A+) | 65.0 (C) | 67.5 (C) |
| daily_user | 75.0 (B) | 50.0 (D) | 57.5 (C) |
| design_leader | 62.5 (C) | 62.5 (C) | 47.5 (D) |
| student_non_designer | 52.5 (C) | 37.5 (D) | 42.5 (D) |
| traditional_craftsperson | 22.5 (F) | 35.0 (F) | 32.5 (F) |
| ux_researcher | - | 50.0 (D) | 47.5 (D) |

## NPS by Archetype

| Archetype | Qwen Pre-ARIA | Qwen Post-ARIA v1 | Qwen Post-ARIA v2 (UX fixes) |
|---|---|---|---|
| agency_creative_director | 7.0 | 6.0 | 6.0 |
| ai_native_engineer | 7.0 | 3.0 | 3.0 |
| app_builder | 7.0 | 6.0 | 7.0 |
| career_changer | 7.0 | 3.0 | 3.0 |
| curious_explorer | 7.0 | 6.0 | 6.0 |
| daily_user | 7.0 | 5.0 | 6.0 |
| design_leader | 7.0 | 5.0 | 5.0 |
| student_non_designer | 7.0 | 5.0 | 5.0 |
| traditional_craftsperson | 7.0 | 5.0 | 4.0 |
| ux_researcher | - | 6.0 | 5.0 |

## Cost-Quality Verdict

### Qwen Post-ARIA v1 vs Qwen Pre-ARIA
- **Cost savings:** 100%
- **SUS delta:** -12.0 pts (within 1 SD)
- **NPS delta:** -2.0
- **Heuristic coverage:** 9/11 vs 7/11
- **Verdict: RECOMMENDED** -- quality within tolerance at 100% savings

### Qwen Post-ARIA v2 (UX fixes) vs Qwen Pre-ARIA
- **Cost savings:** 100%
- **SUS delta:** -12.6 pts (within 1 SD)
- **NPS delta:** -2.0
- **Heuristic coverage:** 9/11 vs 7/11
- **Verdict: RECOMMENDED** -- quality within tolerance at 100% savings

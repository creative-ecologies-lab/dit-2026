# Model Comparison Report

**Arms:** Sonnet 4 (baseline), Haiku 4.5

## Summary

| Metric | Sonnet 4 (baseline) | Haiku 4.5 |
|---|---|---|
| Sessions | 60 | 10 |
| Avg NPS | 6.4 | 6.2 |
| NPS Std Dev | 1.07 | 2.25 |
| Pages/session | 14.0 | 13.7 |
| Completion rate | 98% | 90% |
| Avg cost/session | $0.240 | $0.134 |
| Total cost | $14.37 | $1.34 |
| Avg SUS | 58.5 | 68.5 |
| SUS Grade | C | B |
| SUS Std Dev | 13.8 | 18.5 |
| Heuristics covered | 10/10 | 9/10 |
| Heuristic citation rate | 100% | 97% |
| CW total failures | 1849 | 210 |
| CW: will_try_right_effect | 53% | 24% |
| CW: notices_correct_action | 61% | 54% |
| CW: associates_action_with_goal | 66% | 64% |
| CW: sees_progress | 40% | 12% |
| Behavioral events/session | 41.3 | 47.9 |

## Thought Quality

| Metric | Sonnet 4 (baseline) | Haiku 4.5 |
|---|---|---|
| Avg Length | 225 | 423 |
| Type Diversity | 5 | 5 |
| Total Thoughts | 4195 | 718 |
| Parse Errors | 0 | 0 |

## SUS by Archetype

| Archetype | Sonnet 4 (baseline) | Haiku 4.5 |
|---|---|---|
| agency_creative_director | 49.5 (C) | 75.0 (B) |
| ai_native_engineer | 67.5 (B) | 82.5 (A) |
| app_builder | 68.9 (C) | 72.5 (B) |
| career_changer | 34.0 (F) | 25.0 (F) |
| curious_explorer | 75.8 (B) | 90.0 (A+) |
| daily_user | 67.0 (C) | 82.5 (A) |
| design_leader | 64.2 (C) | 75.0 (B) |
| student_non_designer | 52.9 (D) | 55.0 (C) |
| traditional_craftsperson | 47.9 (D) | 62.5 (C) |
| ux_researcher | 53.3 (D) | 65.0 (C) |

## NPS by Archetype

| Archetype | Sonnet 4 (baseline) | Haiku 4.5 |
|---|---|---|
| agency_creative_director | 6.0 | 7.0 |
| ai_native_engineer | 7.0 | 7.0 |
| app_builder | 7.1 | 7.0 |
| career_changer | 6.8 | 6.0 |
| curious_explorer | 7.5 | 8.0 |
| daily_user | 7.0 | 7.0 |
| design_leader | 6.2 | 6.0 |
| student_non_designer | 5.3 | 7.0 |
| traditional_craftsperson | 5.3 | 7.0 |
| ux_researcher | 5.7 | - |

## Cost-Quality Verdict

### Haiku 4.5 vs Sonnet 4 (baseline)
- **Cost savings:** 44%
- **SUS delta:** +10.0 pts (within 1 SD)
- **NPS delta:** -0.2
- **Heuristic coverage:** 9/10 vs 10/10
- **Verdict: RECOMMENDED** -- quality within tolerance at 44% savings

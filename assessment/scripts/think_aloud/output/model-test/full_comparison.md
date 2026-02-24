# Model Comparison Report

**Arms:** Haiku 4.5 (50 sessions), Haiku 4.5 (10 pilot), Qwen3-32B v2, Qwen3-32B v3 (engineered)

## Summary

| Metric | Haiku 4.5 (50 sessions) | Haiku 4.5 (10 pilot) | Qwen3-32B v2 | Qwen3-32B v3 (engineered) |
|---|---|---|---|---|
| Sessions | 50 | 10 | 10 | 10 |
| Avg NPS | 5.7 | 6.2 | 7.0 | 5.3 |
| NPS Std Dev | 2.83 | 2.25 | 0.0 | 1.25 |
| Pages/session | 8.7 | 13.7 | 12.6 | 12.7 |
| Completion rate | 56% | 90% | 90% | 90% |
| Avg cost/session | $0.083 | $0.134 | $0.000 | $0.000 |
| Total cost | $4.16 | $1.34 | $0.00 | $0.00 |
| Avg SUS | 70.6 | 68.5 | 57.8 | 50.0 |
| SUS Grade | B | B | C | D |
| SUS Std Dev | 16.3 | 18.5 | 18.8 | 18.2 |
| Heuristics covered | 9/10 | 9/10 | 7/10 | 9/10 |
| Heuristic citation rate | 99% | 97% | 100% | 100% |
| CW total failures | 599 | 210 | 75 | 215 |
| CW: will_try_right_effect | 21% | 24% | 10% | 42% |
| CW: notices_correct_action | 44% | 54% | 10% | 31% |
| CW: associates_action_with_goal | 62% | 64% | 24% | 36% |
| CW: sees_progress | 11% | 12% | 15% | 60% |
| Behavioral events/session | 29.0 | 47.9 | 44.9 | 49.7 |

## Thought Quality

| Metric | Haiku 4.5 (50 sessions) | Haiku 4.5 (10 pilot) | Qwen3-32B v2 | Qwen3-32B v3 (engineered) |
|---|---|---|---|---|
| Avg Length | 424 | 423 | 158 | 151 |
| Type Diversity | 5 | 5 | 5 | 5 |
| Total Thoughts | 2283 | 718 | 630 | 635 |
| Parse Errors | 0 | 0 | 0 | 0 |

## SUS by Archetype

| Archetype | Haiku 4.5 (50 sessions) | Haiku 4.5 (10 pilot) | Qwen3-32B v2 | Qwen3-32B v3 (engineered) |
|---|---|---|---|---|
| agency_creative_director | 77.5 (B) | 75.0 (B) | 65.0 (C) | 45.0 (D) |
| ai_native_engineer | 78.8 (B) | 82.5 (A) | 47.5 (D) | 42.5 (D) |
| app_builder | 79.2 (B) | 72.5 (B) | 67.5 (C) | 60.0 (C) |
| career_changer | 37.5 (F) | 25.0 (F) | 42.5 (D) | 22.5 (F) |
| curious_explorer | 78.8 (B) | 90.0 (A+) | 85.0 (A+) | 82.5 (A) |
| daily_user | 87.5 (A+) | 82.5 (A) | 75.0 (B) | 70.0 (B) |
| design_leader | 75.0 (B) | 75.0 (B) | 62.5 (C) | 55.0 (C) |
| student_non_designer | 52.5 (B) | 55.0 (C) | 52.5 (C) | 35.0 (F) |
| traditional_craftsperson | 75.0 (B) | 62.5 (C) | 22.5 (F) | 32.5 (F) |
| ux_researcher | 72.5 (B) | 65.0 (C) | - | 55.0 (C) |

## NPS by Archetype

| Archetype | Haiku 4.5 (50 sessions) | Haiku 4.5 (10 pilot) | Qwen3-32B v2 | Qwen3-32B v3 (engineered) |
|---|---|---|---|---|
| agency_creative_director | 7.0 | 7.0 | 7.0 | 6.0 |
| ai_native_engineer | 7.0 | 7.0 | 7.0 | 3.0 |
| app_builder | 7.0 | 7.0 | 7.0 | 6.0 |
| career_changer | 6.3 | 6.0 | 7.0 | 4.0 |
| curious_explorer | 7.8 | 8.0 | 7.0 | 7.0 |
| daily_user | 7.0 | 7.0 | 7.0 | 7.0 |
| design_leader | 6.0 | 6.0 | 7.0 | 5.0 |
| student_non_designer | 7.0 | 7.0 | 7.0 | 5.0 |
| traditional_craftsperson | 7.0 | 7.0 | 7.0 | 5.0 |
| ux_researcher | 7.0 | - | - | 5.0 |

## Cost-Quality Verdict

### Haiku 4.5 (10 pilot) vs Haiku 4.5 (50 sessions)
- **Cost savings:** -61%
- **SUS delta:** -2.1 pts (within 1 SD)
- **NPS delta:** +0.5
- **Heuristic coverage:** 9/10 vs 9/10
- **Verdict: RECOMMENDED** -- quality within tolerance at -61% savings

### Qwen3-32B v2 vs Haiku 4.5 (50 sessions)
- **Cost savings:** 100%
- **SUS delta:** -12.8 pts (within 1 SD)
- **NPS delta:** +1.3
- **Heuristic coverage:** 7/10 vs 9/10
- **Verdict: NOT RECOMMENDED** -- heuristic coverage too low (7/10)

### Qwen3-32B v3 (engineered) vs Haiku 4.5 (50 sessions)
- **Cost savings:** 100%
- **SUS delta:** -20.6 pts (OUTSIDE 1 SD)
- **NPS delta:** -0.4
- **Heuristic coverage:** 9/10 vs 9/10
- **Verdict: MARGINAL** -- SUS drop outside 1 SD, review qualitatively

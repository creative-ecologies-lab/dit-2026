# Model Comparison Report

**Arms:** Haiku Pre-ARIA (50), Haiku Post-ARIA (10), Qwen Pre-ARIA (10), Qwen Post-ARIA (10)

## Summary

| Metric | Haiku Pre-ARIA (50) | Haiku Post-ARIA (10) | Qwen Pre-ARIA (10) | Qwen Post-ARIA (10) |
|---|---|---|---|---|
| Sessions | 50 | 10 | 10 | 10 |
| Avg NPS | 5.7 | 5.8 | 7.0 | 5.0 |
| NPS Std Dev | 2.83 | 0.63 | 0.0 | 1.15 |
| Pages/session | 8.7 | 13.9 | 12.6 | 12.7 |
| Completion rate | 56% | 100% | 90% | 100% |
| Avg cost/session | $0.083 | $0.167 | $0.000 | $0.000 |
| Total cost | $4.16 | $1.67 | $0.00 | $0.00 |
| Avg SUS | 70.6 | 57.8 | 57.8 | 45.8 |
| SUS Grade | B | C | C | D |
| SUS Std Dev | 16.3 | 13.3 | 18.8 | 12.9 |
| Heuristics covered | 9/11 | 6/11 | 7/11 | 9/11 |
| Heuristic citation rate | 99% | 101% | 100% | 100% |
| CW total failures | 599 | 265 | 75 | 358 |
| CW: will_try_right_effect | 21% | 15% | 10% | 46% |
| CW: notices_correct_action | 44% | 54% | 10% | 61% |
| CW: associates_action_with_goal | 62% | 74% | 24% | 39% |
| CW: sees_progress | 11% | 17% | 15% | 77% |
| CW: understands_page_structure | 0% | 55% | 0% | 59% |
| Behavioral events/session | 29.0 | 42.5 | 44.9 | 47.4 |
| Structure understanding | - | 45% | - | 41% |
| Accessibility rating | - | 3 | - | 2.8 |

## Thought Quality

| Metric | Haiku Pre-ARIA (50) | Haiku Post-ARIA (10) | Qwen Pre-ARIA (10) | Qwen Post-ARIA (10) |
|---|---|---|---|---|
| Avg Length | 424 | 443 | 158 | 150 |
| Type Diversity | 5 | 6 | 5 | 6 |
| Total Thoughts | 2283 | 767 | 630 | 762 |
| Parse Errors | 0 | 0 | 0 | 0 |

## SUS by Archetype

| Archetype | Haiku Pre-ARIA (50) | Haiku Post-ARIA (10) | Qwen Pre-ARIA (10) | Qwen Post-ARIA (10) |
|---|---|---|---|---|
| agency_creative_director | 77.5 (B) | 57.5 (C) | 65.0 (C) | 47.5 (D) |
| ai_native_engineer | 78.8 (B) | 72.5 (B) | 47.5 (D) | 30.0 (F) |
| app_builder | 79.2 (B) | 77.5 (B) | 67.5 (C) | 52.5 (C) |
| career_changer | 37.5 (F) | 42.5 (D) | 42.5 (D) | 27.5 (F) |
| curious_explorer | 78.8 (B) | 67.5 (C) | 85.0 (A+) | 65.0 (C) |
| daily_user | 87.5 (A+) | 47.5 (D) | 75.0 (B) | 50.0 (D) |
| design_leader | 75.0 (B) | 70.0 (B) | 62.5 (C) | 62.5 (C) |
| student_non_designer | 52.5 (B) | 52.5 (C) | 52.5 (C) | 37.5 (D) |
| traditional_craftsperson | 75.0 (B) | 40.0 (D) | 22.5 (F) | 35.0 (F) |
| ux_researcher | 72.5 (B) | 50.0 (D) | - | 50.0 (D) |

## NPS by Archetype

| Archetype | Haiku Pre-ARIA (50) | Haiku Post-ARIA (10) | Qwen Pre-ARIA (10) | Qwen Post-ARIA (10) |
|---|---|---|---|---|
| agency_creative_director | 7.0 | 5.0 | 7.0 | 6.0 |
| ai_native_engineer | 7.0 | 6.0 | 7.0 | 3.0 |
| app_builder | 7.0 | 6.0 | 7.0 | 6.0 |
| career_changer | 6.3 | 6.0 | 7.0 | 3.0 |
| curious_explorer | 7.8 | 7.0 | 7.0 | 6.0 |
| daily_user | 7.0 | 6.0 | 7.0 | 5.0 |
| design_leader | 6.0 | 6.0 | 7.0 | 5.0 |
| student_non_designer | 7.0 | 5.0 | 7.0 | 5.0 |
| traditional_craftsperson | 7.0 | 5.0 | 7.0 | 5.0 |
| ux_researcher | 7.0 | 6.0 | - | 6.0 |

## Cost-Quality Verdict

### Haiku Post-ARIA (10) vs Haiku Pre-ARIA (50)
- **Cost savings:** -100%
- **SUS delta:** -12.8 pts (within 1 SD)
- **NPS delta:** +0.1
- **Heuristic coverage:** 6/11 vs 9/11
- **Verdict: NOT RECOMMENDED** -- heuristic coverage too low (6/11)

### Qwen Pre-ARIA (10) vs Haiku Pre-ARIA (50)
- **Cost savings:** 100%
- **SUS delta:** -12.8 pts (within 1 SD)
- **NPS delta:** +1.3
- **Heuristic coverage:** 7/11 vs 9/11
- **Verdict: NOT RECOMMENDED** -- heuristic coverage too low (7/11)

### Qwen Post-ARIA (10) vs Haiku Pre-ARIA (50)
- **Cost savings:** 100%
- **SUS delta:** -24.8 pts (OUTSIDE 1 SD)
- **NPS delta:** -0.7
- **Heuristic coverage:** 9/11 vs 9/11
- **Verdict: MARGINAL** -- SUS drop outside 1 SD, review qualitatively

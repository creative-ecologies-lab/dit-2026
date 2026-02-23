"""Think-aloud protocol test for DIT Assessment.

v2: Dual-loop architecture (fast observe + slow reflect-and-act),
psychological scaffolds, behavioral realism, SUS scoring,
and self-consistency support.

Usage:
    cd assessment
    python -m scripts.think_aloud                                # dry-run, 3 sessions
    python -m scripts.think_aloud --sessions 50                  # full run
    python -m scripts.think_aloud --sessions 50 --parallel 10    # 10 concurrent sessions
    python -m scripts.think_aloud --persona daily_user -n 1      # single persona debug
    python -m scripts.think_aloud --analyze-only                 # re-run analysis
    python -m scripts.think_aloud --target http://localhost:5002  # local server
"""

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

from .config import (
    DEFAULT_TARGET, DEFAULT_MODEL, DEFAULT_COHORT, MAX_BUDGET_USD,
    HESITATION_DELAY_MS, REREAD_DELAY_MS, MISCLICK_RECOVERY_MS,
)
from .personas import ARCHETYPES, instantiate_personas
from .engine import ThinkAloudEngine, BudgetExceeded
from .recorder import SessionRecorder
from .analyzer import load_sessions, analyze, write_report
from . import driver


OUTPUT_DIR = str(Path(__file__).parent / "output")


async def _dual_loop_observe(
    page,
    persona: dict,
    engine: ThinkAloudEngine,
    recorder: SessionRecorder,
    journey_context: str,
    screenshot_path: str,
    rng: random.Random,
    use_async: bool = False,
):
    """Run dual-loop observation: fast reaction → slow analysis + action.

    Returns (response, fast_reaction, behavioral_events) tuple.
    When use_async=True, uses async engine methods for parallel execution.
    """
    state = await driver.get_page_state(page)
    await driver.save_screenshot(page, screenshot_path)

    behavioral_events = []

    # ── FAST LOOP: immediate gut reaction + CW ──
    if use_async:
        fast_reaction = await engine.observe_fast_async(
            persona, state["a11y_text"], state["url"], journey_context,
        )
    else:
        fast_reaction = engine.observe_fast(
            persona, state["a11y_text"], state["url"], journey_context,
        )

    # ── Behavioral realism: reading speed delay ──
    reading_speed = persona.get("reading_speed", 1.0)
    if reading_speed > 1.0:
        delay = int(REREAD_DELAY_MS * (reading_speed - 1.0))
        await page.wait_for_timeout(delay)
        behavioral_events.append("slow_reader_delay")

    # ── SLOW LOOP: deep analysis + action decision ──
    if use_async:
        response = await engine.reflect_and_act_async(
            persona, state["a11y_text"], state["url"],
            state["interactive_elements"], recorder.action_history,
            journey_context, fast_reaction,
        )
    else:
        response = engine.reflect_and_act(
            persona, state["a11y_text"], state["url"],
            state["interactive_elements"], recorder.action_history,
            journey_context, fast_reaction,
        )

    # ── Behavioral realism: hesitation ──
    hesitation = response.get("action", {}).get("hesitation", "none")
    if hesitation == "significant":
        await page.wait_for_timeout(HESITATION_DELAY_MS)
        behavioral_events.append("significant_hesitation")
        # Re-read: get fresh page state (models re-reading the page)
        behavioral_events.append("re_read")
    elif hesitation == "brief":
        await page.wait_for_timeout(HESITATION_DELAY_MS // 3)
        behavioral_events.append("brief_hesitation")

    # Record the page observation
    recorder.record_page(
        state["url"], response, screenshot_path,
        fast_reaction=fast_reaction,
        behavioral_events=behavioral_events if behavioral_events else None,
    )

    return response, fast_reaction, behavioral_events


async def run_session(
    persona: dict,
    target_url: str,
    cohort: str,
    engine: ThinkAloudEngine,
    headless: bool = True,
    session_num: int = 0,
    total_sessions: int = 1,
    seed: int = 42,
    use_async: bool = False,
):
    """Run a single think-aloud session with one persona."""
    from playwright.async_api import async_playwright

    rng = random.Random(seed + session_num)
    recorder = SessionRecorder(persona, "primary", OUTPUT_DIR)

    prefix = f"[{session_num+1}/{total_sessions}] {persona['archetype_id']}"
    print(f"{prefix}: Starting session {recorder.session_id}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="ThinkAloud-DIT/2.0",
        )
        page = await context.new_page()

        try:
            screenshot_dir = Path(OUTPUT_DIR) / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # ── Landing page ──
            await page.goto(target_url, wait_until="networkidle",
                            timeout=driver.PAGE_LOAD_TIMEOUT_MS)
            await driver.clear_session(page)

            ss_path = str(screenshot_dir / f"{recorder.session_id}_00_landing.png")
            response, _, _ = await _dual_loop_observe(
                page, persona, engine, recorder,
                "You just arrived at the landing page. You're here to take the self-assessment.",
                ss_path, rng, use_async=use_async,
            )
            print(f"{prefix}: Landing page observed")

            # Navigate to assessment
            await page.goto(f"{target_url}/assess?cohort={cohort}",
                            wait_until="networkidle",
                            timeout=driver.PAGE_LOAD_TIMEOUT_MS)
            await driver.clear_session(page)

            # ── Intake ──
            ss_path = str(screenshot_dir / f"{recorder.session_id}_01_intake.png")

            # Behavioral realism: ai_native_engineer may skip intake
            skip_intake = (
                persona["archetype_id"] == "ai_native_engineer"
                and rng.random() < 0.15
            )

            response, _, _ = await _dual_loop_observe(
                page, persona, engine, recorder,
                "You're on the intake page. Fill in optional demographics or skip to start.",
                ss_path, rng, use_async=use_async,
            )

            # Fill intake
            if skip_intake:
                try:
                    await page.click("#intakeSkip", timeout=3000)
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
                print(f"{prefix}: Intake SKIPPED (impatient persona)")
            else:
                try:
                    await page.fill("#intakeCohort", cohort, timeout=3000)
                    if persona.get("age_range") and persona["age_range"] != "":
                        await page.select_option("#intakeAge", persona["age_range"], timeout=3000)
                    await page.fill("#intakeRole", persona["role"], timeout=3000)
                    await page.click("#intakeStart", timeout=3000)
                    await page.wait_for_timeout(500)
                except Exception:
                    try:
                        await page.click("#intakeSkip", timeout=3000)
                        await page.wait_for_timeout(500)
                    except Exception:
                        pass
                print(f"{prefix}: Intake completed")

            # ── SAE Questions (6) ──
            for q_idx in range(6):
                await page.wait_for_timeout(300)
                stage = await driver.get_current_stage(page)
                if stage != "sae":
                    break

                ss_path = str(screenshot_dir / f"{recorder.session_id}_02_sae_{q_idx}.png")
                response, fast_rx, b_events = await _dual_loop_observe(
                    page, persona, engine, recorder,
                    f"SAE Question {q_idx+1} of 6. Pick the automation level that best describes YOUR work.",
                    ss_path, rng, use_async=use_async,
                )

                # Execute the LLM's chosen action
                action = response.get("action", {})

                # ── Behavioral realism: misclick ──
                misclick_events = []
                if rng.random() < persona.get("confusion_prob", 0):
                    misclick_events.append("misclick")
                    # Click wrong adjacent option first
                    try:
                        correct_val = action.get("value", "")
                        if correct_val.isdigit():
                            wrong_val = str(max(0, min(5,
                                int(correct_val) + rng.choice([-1, 1]))))
                            await page.click(
                                f'label.option-item:has(input[value="{wrong_val}"])',
                                timeout=2000)
                            await page.wait_for_timeout(MISCLICK_RECOVERY_MS)
                            misclick_events.append("misclick_corrected")
                    except Exception:
                        pass

                if misclick_events:
                    recorder.behavioral_events.extend(
                        {"event": e, "url": page.url} for e in misclick_events
                    )

                err = await driver.execute_action(page, action)
                if err:
                    # Fallback: pick based on persona's SAE center
                    sae_val = max(0, min(5, round(rng.gauss(
                        persona["sae_center"], persona["sae_spread"]))))
                    try:
                        await page.click(
                            f'label.option-item:has(input[value="{sae_val}"])',
                            timeout=3000)
                        await page.wait_for_timeout(driver.WAIT_AFTER_CLICK_MS)
                    except Exception:
                        pass

                print(f"{prefix}: SAE Q{q_idx+1} answered")

            # Wait for EPIAS stage
            await driver.wait_for_stage(page, "#epiasStage", timeout=5000)

            # ── EPIAS Questions (5) ──
            epias_letters = ["E", "P", "I", "A", "S"]
            for q_idx in range(5):
                await page.wait_for_timeout(300)
                stage = await driver.get_current_stage(page)
                if stage not in ("epias", "sae"):
                    break

                ss_path = str(screenshot_dir / f"{recorder.session_id}_03_epias_{q_idx}.png")
                response, fast_rx, b_events = await _dual_loop_observe(
                    page, persona, engine, recorder,
                    f"EPIAS Question {q_idx+1} of 5. Pick the maturity stage that best describes HOW you work.",
                    ss_path, rng, use_async=use_async,
                )

                action = response.get("action", {})

                # ── Behavioral realism: misclick ──
                misclick_events = []
                if rng.random() < persona.get("confusion_prob", 0):
                    misclick_events.append("misclick")
                    try:
                        correct_val = action.get("value", "")
                        if correct_val in epias_letters:
                            idx = epias_letters.index(correct_val)
                            wrong_idx = max(0, min(4, idx + rng.choice([-1, 1])))
                            wrong_val = epias_letters[wrong_idx]
                            await page.click(
                                f'label.option-item:has(input[value="{wrong_val}"])',
                                timeout=2000)
                            await page.wait_for_timeout(MISCLICK_RECOVERY_MS)
                            misclick_events.append("misclick_corrected")
                    except Exception:
                        pass

                if misclick_events:
                    recorder.behavioral_events.extend(
                        {"event": e, "url": page.url} for e in misclick_events
                    )

                err = await driver.execute_action(page, action)
                if err:
                    # Fallback: pick based on persona's EPIAS center
                    idx = max(0, min(4, round(rng.gauss(
                        persona["epias_center"] - 1, persona["epias_spread"]))))
                    letter = epias_letters[idx]
                    try:
                        await page.click(
                            f'label.option-item:has(input[value="{letter}"])',
                            timeout=3000)
                        await page.wait_for_timeout(driver.WAIT_AFTER_CLICK_MS)
                    except Exception:
                        pass

                print(f"{prefix}: EPIAS Q{q_idx+1} answered")

            # ── Wait for results ──
            try:
                await page.wait_for_url("**/results**", timeout=10000)
            except Exception:
                try:
                    await page.click("text=See Results", timeout=3000)
                    await page.wait_for_url("**/results**", timeout=10000)
                except Exception:
                    pass

            await page.wait_for_timeout(1000)

            # ── Results page ──
            ss_path = str(screenshot_dir / f"{recorder.session_id}_04_results.png")
            response, _, _ = await _dual_loop_observe(
                page, persona, engine, recorder,
                "You're viewing your results. React to your placement and the growth path suggestions.",
                ss_path, rng, use_async=use_async,
            )

            # Capture the actual result from sessionStorage
            try:
                result_json = await page.evaluate(
                    "sessionStorage.getItem('ditResult')")
                if result_json:
                    recorder.record_result(json.loads(result_json))
            except Exception:
                pass

            print(f"{prefix}: Results observed")

            # ── Final reflection ──
            summary = recorder.transcript_summary()
            if use_async:
                reflection = await engine.reflect_async(persona, summary)
            else:
                reflection = engine.reflect(persona, summary)
            recorder.record_reflection(reflection)
            print(f"{prefix}: Reflection generated")

            # ── SUS Questionnaire ──
            if use_async:
                sus_data = await engine.score_sus_async(persona, summary)
            else:
                sus_data = engine.score_sus(persona, summary)
            recorder.record_sus(sus_data)
            sus_score = sus_data.get("sus_total", "?")
            sus_grade = sus_data.get("sus_grade", "?")
            print(f"{prefix}: SUS scored: {sus_score} (Grade {sus_grade})")

        except BudgetExceeded as e:
            print(f"{prefix}: {e}")
        except Exception as e:
            print(f"{prefix}: ERROR: {e}")
        finally:
            await browser.close()

    path = recorder.save()
    print(f"{prefix}: Saved to {path} | Cost so far: ${engine.cost_usd:.3f}")
    return recorder


async def main():
    parser = argparse.ArgumentParser(description="Think-aloud protocol test v2")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target URL")
    parser.add_argument("--sessions", "-n", type=int, default=3,
                        help="Number of sessions to run")
    parser.add_argument("--cohort", default=DEFAULT_COHORT, help="Cohort code")
    parser.add_argument("--persona", type=str, default=None,
                        help="Run single persona archetype by ID")
    parser.add_argument("--analyze-only", action="store_true",
                        help="Only run analysis on existing sessions")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--budget", type=float, default=MAX_BUDGET_USD,
                        help="Budget cap in USD")
    parser.add_argument("--parallel", "-p", type=int, default=1,
                        help="Max concurrent sessions (default: 1 = sequential)")
    args = parser.parse_args()

    # Analysis-only mode
    if args.analyze_only:
        print("Loading existing sessions...")
        sessions = load_sessions(OUTPUT_DIR)
        if not sessions:
            print("No sessions found. Run some sessions first.")
            sys.exit(1)
        print(f"Loaded {len(sessions)} sessions. Analyzing...")
        results = analyze(sessions)
        report_path = write_report(results, OUTPUT_DIR)
        print(f"Report written to: {report_path}")
        print(f"\nSummary: {json.dumps(results['summary'], indent=2)}")
        sys.exit(0)

    # Generate personas
    if args.persona:
        # Single archetype mode
        matching = [a for a in ARCHETYPES if a["id"] == args.persona]
        if not matching:
            print(f"Unknown persona: {args.persona}")
            print(f"Available: {', '.join(a['id'] for a in ARCHETYPES)}")
            sys.exit(1)
        all_personas = instantiate_personas(n_per_archetype=args.sessions, seed=args.seed)
        personas = [p for p in all_personas if p["archetype_id"] == args.persona][:args.sessions]
    else:
        # Distribute across archetypes
        n_per = max(1, args.sessions // len(ARCHETYPES))
        remainder = args.sessions - n_per * len(ARCHETYPES)
        personas = instantiate_personas(n_per_archetype=n_per, seed=args.seed)
        if remainder > 0:
            extras = instantiate_personas(n_per_archetype=1, seed=args.seed + 1)
            personas.extend(extras[:remainder])
        personas = personas[:args.sessions]

    print(f"Think-Aloud Protocol v2 Test")
    print(f"  Target: {args.target}")
    print(f"  Sessions: {len(personas)}")
    print(f"  Model: {args.model}")
    print(f"  Cohort: {args.cohort}")
    print(f"  Budget: ${args.budget:.2f}")
    concurrency = max(1, args.parallel)
    print(f"  Architecture: Dual-loop (fast observe -> slow reflect)")
    print(f"  Concurrency: {concurrency} {'(parallel)' if concurrency > 1 else '(sequential)'}")
    print()

    engine = ThinkAloudEngine(model=args.model, budget=args.budget)

    if concurrency == 1:
        # Sequential execution (original behavior)
        for i, persona in enumerate(personas):
            try:
                await run_session(
                    persona, args.target, args.cohort, engine,
                    headless=args.headless, session_num=i,
                    total_sessions=len(personas), seed=args.seed,
                )
            except BudgetExceeded:
                print(f"\nBudget exceeded after {i+1} sessions. Stopping.")
                break
            except Exception as e:
                print(f"Session {i+1} failed: {e}")
                continue
    else:
        # Parallel execution with semaphore-limited concurrency
        semaphore = asyncio.Semaphore(concurrency)
        completed = 0
        failed = 0
        budget_hit = False

        async def _run_one(i, persona):
            nonlocal completed, failed, budget_hit
            if budget_hit:
                return
            async with semaphore:
                if budget_hit:
                    return
                try:
                    await run_session(
                        persona, args.target, args.cohort, engine,
                        headless=args.headless, session_num=i,
                        total_sessions=len(personas), seed=args.seed,
                        use_async=True,
                    )
                    completed += 1
                except BudgetExceeded:
                    budget_hit = True
                    print(f"\nBudget exceeded. Stopping new sessions.")
                except Exception as e:
                    failed += 1
                    print(f"Session {i+1} failed: {e}")

        tasks = [_run_one(i, p) for i, p in enumerate(personas)]
        await asyncio.gather(*tasks)
        print(f"\nParallel run complete: {completed} succeeded, {failed} failed")

    # Usage summary
    usage = engine.usage_summary()
    print(f"\n{'='*50}")
    print(f"USAGE SUMMARY")
    print(f"  API calls: {usage['calls']}")
    print(f"  Input tokens: {usage['input_tokens']:,}")
    print(f"  Output tokens: {usage['output_tokens']:,}")
    print(f"  Total cost: ${usage['cost_usd']:.3f}")
    print(f"  Budget remaining: ${usage['budget_remaining']:.3f}")
    print(f"  Cost per session: ${usage['cost_usd'] / max(1, len(personas)):.3f}")

    # Run analysis
    sessions = load_sessions(OUTPUT_DIR)
    if sessions:
        print(f"\nAnalyzing {len(sessions)} sessions...")
        results = analyze(sessions)
        report_path = write_report(results, OUTPUT_DIR)
        print(f"Report: {report_path}")
        print(f"Avg NPS: {results['summary']['avg_nps']}")
        print(f"Completion rate: {results['flow_completion']['completion_rate']:.0%}")

        # v2 summary stats
        if "sus_analysis" in results:
            sus = results["sus_analysis"]
            print(f"Avg SUS: {sus.get('overall_mean', '?')} "
                  f"(Grade {sus.get('overall_grade', '?')})")
        if "heuristic_analysis" in results:
            h = results["heuristic_analysis"]
            print(f"Heuristic coverage: {h.get('heuristics_covered', '?')}/10")
        if "behavioral_realism" in results:
            b = results["behavioral_realism"]
            print(f"Behavioral events/session: {b.get('events_per_session', '?')}")


if __name__ == "__main__":
    asyncio.run(main())

"""Think-aloud protocol test for DIT Assessment.

Simulates users with diverse personas taking the assessment while
articulating their thoughts — producing structured usability feedback.

Usage:
    cd assessment
    python -m scripts.think_aloud                                # dry-run, 3 sessions
    python -m scripts.think_aloud --sessions 50                  # full run
    python -m scripts.think_aloud --persona daily_user -n 1      # single persona debug
    python -m scripts.think_aloud --analyze-only                 # re-run analysis
    python -m scripts.think_aloud --target http://localhost:5002  # local server
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .config import DEFAULT_TARGET, DEFAULT_MODEL, DEFAULT_COHORT, MAX_BUDGET_USD
from .personas import ARCHETYPES, instantiate_personas
from .engine import ThinkAloudEngine, BudgetExceeded
from .recorder import SessionRecorder
from .analyzer import load_sessions, analyze, write_report
from . import driver


OUTPUT_DIR = str(Path(__file__).parent / "output")


async def run_session(
    persona: dict,
    target_url: str,
    cohort: str,
    engine: ThinkAloudEngine,
    headless: bool = True,
    session_num: int = 0,
    total_sessions: int = 1,
):
    """Run a single think-aloud session with one persona."""
    from playwright.async_api import async_playwright

    recorder = SessionRecorder(persona, "primary", OUTPUT_DIR)

    prefix = f"[{session_num+1}/{total_sessions}] {persona['archetype_id']}"
    print(f"{prefix}: Starting session {recorder.session_id}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="ThinkAloud-DIT/1.0",
        )
        page = await context.new_page()

        try:
            # ── Landing page ──
            await page.goto(target_url, wait_until="networkidle",
                            timeout=driver.PAGE_LOAD_TIMEOUT_MS)
            await driver.clear_session(page)

            state = await driver.get_page_state(page)
            screenshot_dir = Path(OUTPUT_DIR) / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            ss_path = str(screenshot_dir / f"{recorder.session_id}_00_landing.png")
            await driver.save_screenshot(page, ss_path)

            response = engine.observe_and_act(
                persona, state["a11y_text"], state["url"],
                state["interactive_elements"], recorder.action_history,
                "You just arrived at the landing page. You're here to take the self-assessment.",
            )
            recorder.record_page(state["url"], response, ss_path)
            print(f"{prefix}: Landing page observed")

            # Navigate to assessment
            await page.goto(f"{target_url}/assess?cohort={cohort}",
                            wait_until="networkidle",
                            timeout=driver.PAGE_LOAD_TIMEOUT_MS)
            await driver.clear_session(page)

            # ── Intake ──
            state = await driver.get_page_state(page)
            ss_path = str(screenshot_dir / f"{recorder.session_id}_01_intake.png")
            await driver.save_screenshot(page, ss_path)

            response = engine.observe_and_act(
                persona, state["a11y_text"], state["url"],
                state["interactive_elements"], recorder.action_history,
                "You're on the intake page. Fill in optional demographics or skip to start.",
            )
            recorder.record_page(state["url"], response, ss_path)

            # Fill intake — use persona data directly rather than relying on LLM selector
            try:
                await page.fill("#intakeCohort", cohort, timeout=3000)
                if persona.get("age_range") and persona["age_range"] != "":
                    await page.select_option("#intakeAge", persona["age_range"], timeout=3000)
                await page.fill("#intakeRole", persona["role"], timeout=3000)
                await page.click("#intakeStart", timeout=3000)
                await page.wait_for_timeout(500)
            except Exception:
                # Fall back to skip
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

                state = await driver.get_page_state(page)
                ss_path = str(screenshot_dir / f"{recorder.session_id}_02_sae_{q_idx}.png")
                await driver.save_screenshot(page, ss_path)

                response = engine.observe_and_act(
                    persona, state["a11y_text"], state["url"],
                    state["interactive_elements"], recorder.action_history,
                    f"SAE Question {q_idx+1} of 6. Pick the automation level that best describes YOUR work.",
                )
                recorder.record_page(state["url"], response, ss_path)

                # Execute the LLM's chosen action
                action = response.get("action", {})
                err = await driver.execute_action(page, action)
                if err:
                    # Fallback: pick an option based on persona's SAE center
                    import random
                    sae_val = max(0, min(5, round(random.gauss(
                        persona["sae_center"], persona["sae_spread"]))))
                    try:
                        await page.click(
                            f'label.option-item:has(input[value="{sae_val}"])',
                            timeout=3000)
                        await page.wait_for_timeout(driver.WAIT_AFTER_CLICK_MS)
                    except Exception:
                        pass

                print(f"{prefix}: SAE Q{q_idx+1} answered")

            # Wait for EPIAS stage to appear
            await driver.wait_for_stage(page, "#epiasStage", timeout=5000)

            # ── EPIAS Questions (5) ──
            epias_letters = ["E", "P", "I", "A", "S"]
            for q_idx in range(5):
                await page.wait_for_timeout(300)
                stage = await driver.get_current_stage(page)
                if stage not in ("epias", "sae"):
                    break

                state = await driver.get_page_state(page)
                ss_path = str(screenshot_dir / f"{recorder.session_id}_03_epias_{q_idx}.png")
                await driver.save_screenshot(page, ss_path)

                response = engine.observe_and_act(
                    persona, state["a11y_text"], state["url"],
                    state["interactive_elements"], recorder.action_history,
                    f"EPIAS Question {q_idx+1} of 5. Pick the maturity stage that best describes HOW you work.",
                )
                recorder.record_page(state["url"], response, ss_path)

                action = response.get("action", {})
                err = await driver.execute_action(page, action)
                if err:
                    # Fallback: pick based on persona's EPIAS center
                    import random
                    idx = max(0, min(4, round(random.gauss(
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
            # The assessment auto-submits after the last EPIAS question
            try:
                await page.wait_for_url("**/results**", timeout=10000)
            except Exception:
                # Try clicking "See Results" if present
                try:
                    await page.click("text=See Results", timeout=3000)
                    await page.wait_for_url("**/results**", timeout=10000)
                except Exception:
                    pass

            await page.wait_for_timeout(1000)

            # ── Results page ──
            state = await driver.get_page_state(page)
            ss_path = str(screenshot_dir / f"{recorder.session_id}_04_results.png")
            await driver.save_screenshot(page, ss_path)

            response = engine.observe_and_act(
                persona, state["a11y_text"], state["url"],
                state["interactive_elements"], recorder.action_history,
                "You're viewing your results. React to your placement and the growth path suggestions.",
            )
            recorder.record_page(state["url"], response, ss_path)

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
            reflection = engine.reflect(persona, summary)
            recorder.record_reflection(reflection)
            print(f"{prefix}: Reflection generated")

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
    parser = argparse.ArgumentParser(description="Think-aloud protocol test")
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
        # Instantiate this archetype N times
        from .personas import instantiate_personas
        all_personas = instantiate_personas(n_per_archetype=args.sessions, seed=args.seed)
        personas = [p for p in all_personas if p["archetype_id"] == args.persona][:args.sessions]
    else:
        # Distribute across archetypes
        n_per = max(1, args.sessions // len(ARCHETYPES))
        remainder = args.sessions - n_per * len(ARCHETYPES)
        personas = instantiate_personas(n_per_archetype=n_per, seed=args.seed)
        if remainder > 0:
            # Add extras from the beginning
            extras = instantiate_personas(n_per_archetype=1, seed=args.seed + 1)
            personas.extend(extras[:remainder])
        personas = personas[:args.sessions]

    print(f"Think-Aloud Protocol Test")
    print(f"  Target: {args.target}")
    print(f"  Sessions: {len(personas)}")
    print(f"  Model: {args.model}")
    print(f"  Cohort: {args.cohort}")
    print(f"  Budget: ${args.budget:.2f}")
    print()

    engine = ThinkAloudEngine(model=args.model, budget=args.budget)

    for i, persona in enumerate(personas):
        try:
            await run_session(
                persona, args.target, args.cohort, engine,
                headless=args.headless, session_num=i,
                total_sessions=len(personas),
            )
        except BudgetExceeded:
            print(f"\nBudget exceeded after {i+1} sessions. Stopping.")
            break
        except Exception as e:
            print(f"Session {i+1} failed: {e}")
            continue

    # Usage summary
    usage = engine.usage_summary()
    print(f"\n{'='*50}")
    print(f"USAGE SUMMARY")
    print(f"  API calls: {usage['calls']}")
    print(f"  Input tokens: {usage['input_tokens']:,}")
    print(f"  Output tokens: {usage['output_tokens']:,}")
    print(f"  Total cost: ${usage['cost_usd']:.3f}")
    print(f"  Budget remaining: ${usage['budget_remaining']:.3f}")

    # Run analysis
    sessions = load_sessions(OUTPUT_DIR)
    if sessions:
        print(f"\nAnalyzing {len(sessions)} sessions...")
        results = analyze(sessions)
        report_path = write_report(results, OUTPUT_DIR)
        print(f"Report: {report_path}")
        print(f"Avg NPS: {results['summary']['avg_nps']}")
        print(f"Completion rate: {results['flow_completion']['completion_rate']:.0%}")


if __name__ == "__main__":
    asyncio.run(main())

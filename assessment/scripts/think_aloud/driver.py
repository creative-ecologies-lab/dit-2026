"""Playwright browser automation for the DIT assessment."""

import json
from playwright.async_api import Page
from .config import WAIT_AFTER_CLICK_MS, WAIT_FOR_NAVIGATION_MS, PAGE_LOAD_TIMEOUT_MS


def _flatten_a11y_tree(node: dict, depth: int = 0, max_depth: int = 5) -> str:
    """Flatten accessibility tree into readable text."""
    if depth > max_depth:
        return ""

    indent = "  " * depth
    role = node.get("role", "")
    name = node.get("name", "")
    value = node.get("value", "")

    # Skip generic or empty nodes
    if role in ("none", "generic", "presentation") and not name:
        parts = []
        for child in node.get("children", []):
            parts.append(_flatten_a11y_tree(child, depth, max_depth))
        return "\n".join(p for p in parts if p)

    line = f"{indent}[{role}]"
    if name:
        line += f' "{name}"'
    if value:
        line += f" value={value}"

    # Include relevant states
    for key in ("checked", "selected", "disabled", "expanded", "pressed"):
        if key in node:
            line += f" {key}={node[key]}"

    parts = [line]
    for child in node.get("children", []):
        child_text = _flatten_a11y_tree(child, depth + 1, max_depth)
        if child_text:
            parts.append(child_text)

    return "\n".join(parts)


async def get_page_state(page: Page) -> dict:
    """Capture current page state for LLM consumption."""
    # Get accessibility tree
    try:
        a11y = await page.accessibility.snapshot()
        a11y_text = _flatten_a11y_tree(a11y) if a11y else "(empty page)"
    except Exception:
        a11y_text = "(accessibility tree unavailable)"

    # Truncate if very long
    if len(a11y_text) > 6000:
        a11y_text = a11y_text[:6000] + "\n... (truncated)"

    # Get interactive elements
    interactive = await page.evaluate("""() => {
        const elements = [];
        // Buttons
        document.querySelectorAll('button, a.btn, [role="button"]').forEach(el => {
            if (el.offsetParent !== null) {
                elements.push({
                    tag: el.tagName.toLowerCase(),
                    text: el.textContent.trim().substring(0, 80),
                    id: el.id || null,
                    classes: el.className.substring(0, 100),
                    href: el.href || null,
                });
            }
        });
        // Radio/option items
        document.querySelectorAll('label.option-item').forEach(el => {
            if (el.offsetParent !== null) {
                const input = el.querySelector('input');
                elements.push({
                    tag: 'option-item',
                    text: el.textContent.trim().substring(0, 120),
                    value: input ? input.value : null,
                    name: input ? input.name : null,
                    selected: el.classList.contains('selected'),
                });
            }
        });
        // Form inputs
        document.querySelectorAll('input:not([type="radio"]):not([type="hidden"]), select, textarea').forEach(el => {
            if (el.offsetParent !== null) {
                elements.push({
                    tag: el.tagName.toLowerCase(),
                    type: el.type || null,
                    id: el.id || null,
                    value: el.value || null,
                    placeholder: el.placeholder || null,
                });
            }
        });
        // Links (nav)
        document.querySelectorAll('.nav-links a').forEach(el => {
            elements.push({
                tag: 'nav-link',
                text: el.textContent.trim(),
                href: el.href,
                active: el.classList.contains('active'),
            });
        });
        return elements;
    }""")

    interactive_text = json.dumps(interactive, indent=2) if interactive else "(no interactive elements found)"
    if len(interactive_text) > 3000:
        interactive_text = interactive_text[:3000] + "\n... (truncated)"

    return {
        "a11y_text": a11y_text,
        "url": page.url,
        "interactive_elements": interactive_text,
    }


async def save_screenshot(page: Page, path: str):
    """Save screenshot to disk for human review (not sent to LLM)."""
    try:
        await page.screenshot(path=path, full_page=False)
    except Exception:
        pass


async def execute_action(page: Page, action: dict):
    """Execute an LLM-decided action on the page."""
    action_type = action.get("type", "click")
    selector = action.get("selector", "")
    value = action.get("value", "")

    try:
        if action_type == "click":
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(WAIT_AFTER_CLICK_MS)

        elif action_type == "type":
            await page.fill(selector, value, timeout=5000)

        elif action_type == "select":
            await page.select_option(selector, value, timeout=5000)

        elif action_type == "navigate":
            target = value or selector
            if not target.startswith("http"):
                # Relative URL
                base = page.url.rsplit("/", 1)[0] if "/" in page.url else page.url
                target = base.rstrip("/") + "/" + target.lstrip("/")
            await page.goto(target, timeout=PAGE_LOAD_TIMEOUT_MS,
                            wait_until="networkidle")

        elif action_type == "scroll":
            await page.evaluate("window.scrollBy(0, 400)")
            await page.wait_for_timeout(300)

    except Exception as e:
        return f"Action failed: {e}"

    return None


async def wait_for_stage(page: Page, stage_selector: str, timeout: int = 5000):
    """Wait for a stage element to become visible."""
    try:
        await page.wait_for_selector(stage_selector, state="visible", timeout=timeout)
    except Exception:
        pass


async def clear_session(page: Page):
    """Clear sessionStorage for a fresh assessment."""
    await page.evaluate("sessionStorage.clear()")


async def get_current_stage(page: Page) -> str:
    """Detect which assessment stage is currently visible."""
    return await page.evaluate("""() => {
        if (document.querySelector('#intakeStage') &&
            document.querySelector('#intakeStage').style.display !== 'none')
            return 'intake';
        if (document.querySelector('#saeStage') &&
            document.querySelector('#saeStage').style.display !== 'none')
            return 'sae';
        if (document.querySelector('#epiasStage') &&
            document.querySelector('#epiasStage').style.display !== 'none')
            return 'epias';
        if (document.querySelector('#loadingStage') &&
            document.querySelector('#loadingStage').style.display !== 'none')
            return 'loading';
        if (document.querySelector('#completedStage') &&
            document.querySelector('#completedStage').style.display !== 'none')
            return 'completed';
        return 'unknown';
    }""")

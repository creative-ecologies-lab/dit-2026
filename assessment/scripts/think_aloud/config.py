"""Configuration for think-aloud protocol test."""

DEFAULT_TARGET = "https://dit-maeda.noahratzan.com"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_COHORT = "think-aloud-test"
MAX_BUDGET_USD = 20.0

# Pricing per million tokens (Claude Sonnet 4)
INPUT_COST_PER_MTOK = 3.0
OUTPUT_COST_PER_MTOK = 15.0

# Browser timing
WAIT_AFTER_CLICK_MS = 600      # Covers 300ms auto-advance + render
WAIT_FOR_NAVIGATION_MS = 3000
PAGE_LOAD_TIMEOUT_MS = 10000

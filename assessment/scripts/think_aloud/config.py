"""Configuration for think-aloud protocol test."""

PROTOCOL_VERSION = "2.0"

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
PAGE_LOAD_TIMEOUT_MS = 30000

# ── v2: Nielsen's 10 Usability Heuristics ──
NIELSEN_HEURISTICS = [
    "visibility_of_system_status",
    "match_real_world",
    "user_control_freedom",
    "consistency_standards",
    "error_prevention",
    "recognition_over_recall",
    "flexibility_efficiency",
    "minimalist_design",
    "error_recovery",
    "help_documentation",
]

# ── v2: SUS Benchmarking (Brooke, 1996) ──
SUS_BENCHMARK_AVERAGE = 68.0     # Industry average
SUS_GRADE_THRESHOLDS = {
    "A+": 84.1,  # Top 10%
    "A": 80.3,   # Top 15%
    "B": 68.0,   # Average
    "C": 51.0,   # Below average
    "D": 35.7,   # Poor
    "F": 0.0,    # Worst quartile
}

# ── v2: Behavioral realism ──
HESITATION_DELAY_MS = 2000       # Extra wait when persona hesitates
REREAD_DELAY_MS = 1500           # Extra wait when re-reading page
MISCLICK_RECOVERY_MS = 800       # Delay before correcting a misclick

"""Configuration for think-aloud protocol test."""

PROTOCOL_VERSION = "2.1"

DEFAULT_TARGET = "https://dit-maeda.noahratzan.com"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_COHORT = "think-aloud-test"
MAX_BUDGET_USD = 20.0

# Pricing per million tokens (Claude Sonnet 4 — default)
INPUT_COST_PER_MTOK = 3.0
OUTPUT_COST_PER_MTOK = 15.0

# Model pricing lookup (input $/MTok, output $/MTok)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": (3.0, 15.0),
    "claude-3-5-haiku-20241022": (0.80, 4.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
}

# ── Open-source models (self-hosted via vLLM on Modal) ──
OPEN_SOURCE_MODELS = {
    "qwen3-32b": {
        "hf_name": "Qwen/Qwen3-32B",
        "gpu": "A100:1",          # 80GB VRAM needed for BF16
        "est_tokens_per_sec": 1000,
        "gpu_cost_per_hr": 2.50,  # Modal A100 80GB
    },
    "qwen3-14b": {
        "hf_name": "Qwen/Qwen3-14B",
        "gpu": "L40S:1",          # 48GB VRAM, fits BF16
        "est_tokens_per_sec": 2400,
        "gpu_cost_per_hr": 1.95,  # Modal L40S
    },
}

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
    "accessibility_structure",
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

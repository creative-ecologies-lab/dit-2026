"""Model catalog — defines every available model, its provider, and reasoning parameters."""

MODEL_CATALOG = {
    # ── OpenAI (Responses API) ──────────────────────────────────────
    "gpt-5.2": {
        "provider": "openai",
        "label": "GPT-5.2",
        "description": "Latest flagship — strongest reasoning",
        "reasoning_param": "effort",
        "reasoning_options": ["none", "low", "medium", "high", "xhigh"],
        "reasoning_default": "high",
    },
    "gpt-5.1": {
        "provider": "openai",
        "label": "GPT-5.1",
        "description": "Strong general purpose",
        "reasoning_param": "effort",
        "reasoning_options": ["none", "low", "medium", "high"],
        "reasoning_default": "high",
    },
    "gpt-4.1": {
        "provider": "openai",
        "label": "GPT-4.1",
        "description": "Coding and instruction specialist",
        "reasoning_param": None,
    },
    "gpt-4.1-mini": {
        "provider": "openai",
        "label": "GPT-4.1 Mini",
        "description": "Fast and affordable",
        "reasoning_param": None,
    },
    "gpt-5-mini": {
        "provider": "openai",
        "label": "GPT-5 Mini",
        "description": "Fast GPT-5 class model",
        "reasoning_param": "effort",
        "reasoning_options": ["none", "low", "medium", "high"],
        "reasoning_default": "medium",
    },
    "o3": {
        "provider": "openai",
        "label": "o3",
        "description": "Frontier reasoning model",
        "reasoning_param": "effort",
        "reasoning_options": ["low", "medium", "high"],
        "reasoning_default": "medium",
    },
    "o4-mini": {
        "provider": "openai",
        "label": "o4-mini",
        "description": "Fast reasoning model",
        "reasoning_param": "effort",
        "reasoning_options": ["low", "medium", "high"],
        "reasoning_default": "medium",
    },
    # ── Anthropic (Messages API) ────────────────────────────────────
    "claude-opus-4-6": {
        "provider": "anthropic",
        "label": "Claude Opus 4.6",
        "description": "Latest flagship — 1M context, adaptive thinking",
        "reasoning_param": "thinking",
        "reasoning_options": ["off", "1024", "4096", "10000", "32000"],
        "reasoning_labels": {
            "off": "Off", "1024": "1K tokens", "4096": "4K tokens",
            "10000": "10K tokens", "32000": "32K tokens",
        },
        "reasoning_default": "off",
    },
    "claude-sonnet-4-5": {
        "provider": "anthropic",
        "label": "Claude Sonnet 4.5",
        "description": "Strong general purpose",
        "reasoning_param": "thinking",
        "reasoning_options": ["off", "1024", "4096", "10000", "32000"],
        "reasoning_labels": {
            "off": "Off", "1024": "1K tokens", "4096": "4K tokens",
            "10000": "10K tokens", "32000": "32K tokens",
        },
        "reasoning_default": "off",
    },
    "claude-haiku-4-5": {
        "provider": "anthropic",
        "label": "Claude Haiku 4.5",
        "description": "Fast and affordable",
        "reasoning_param": "thinking",
        "reasoning_options": ["off", "1024", "4096", "10000"],
        "reasoning_labels": {
            "off": "Off", "1024": "1K tokens",
            "4096": "4K tokens", "10000": "10K tokens",
        },
        "reasoning_default": "off",
    },
    # ── Google (Generative AI) ──────────────────────────────────────
    "gemini-2.5-pro": {
        "provider": "google",
        "label": "Gemini 2.5 Pro",
        "description": "Strong reasoning",
        "reasoning_param": "thinking_budget",
        "reasoning_options": ["0", "1024", "4096", "8192", "-1"],
        "reasoning_labels": {
            "0": "Off", "1024": "Low (1K)", "4096": "Medium (4K)",
            "8192": "High (8K)", "-1": "Dynamic",
        },
        "reasoning_default": "-1",
    },
    "gemini-2.5-flash": {
        "provider": "google",
        "label": "Gemini 2.5 Flash",
        "description": "Fast and affordable",
        "reasoning_param": "thinking_budget",
        "reasoning_options": ["0", "1024", "4096", "8192", "-1"],
        "reasoning_labels": {
            "0": "Off", "1024": "Low (1K)", "4096": "Medium (4K)",
            "8192": "High (8K)", "-1": "Dynamic",
        },
        "reasoning_default": "-1",
    },
    "gemini-3-pro-preview": {
        "provider": "google",
        "label": "Gemini 3 Pro (Preview)",
        "description": "Latest reasoning model",
        "reasoning_param": "thinking_level",
        "reasoning_options": ["low", "high"],
        "reasoning_default": "high",
    },
    "gemini-3-flash-preview": {
        "provider": "google",
        "label": "Gemini 3 Flash (Preview)",
        "description": "Latest fast model",
        "reasoning_param": "thinking_level",
        "reasoning_options": ["minimal", "low", "medium", "high"],
        "reasoning_default": "medium",
    },
    # ── Groq (OpenAI-compatible, LPU hardware) ───────────────────────
    "qwen/qwen3-32b": {
        "provider": "groq",
        "label": "Qwen3 32B",
        "description": "Open-source 32B model on Groq — fast inference, 131K context",
        "reasoning_param": None,
    },
}


def get_models_for_provider(provider_name: str) -> dict:
    """Return {model_id: model_info} for a given provider."""
    return {
        mid: info for mid, info in MODEL_CATALOG.items()
        if info["provider"] == provider_name
    }


def get_model_info(model_id: str) -> dict | None:
    """Return model info dict or None."""
    return MODEL_CATALOG.get(model_id)

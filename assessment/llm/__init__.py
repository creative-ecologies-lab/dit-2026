"""LLM provider registry with auto-detection."""
from llm.base import LLMProvider, LLMResponse
from llm.models import MODEL_CATALOG, get_models_for_provider


class ProviderRegistry:
    """Registry of LLM providers with auto-detection."""

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider):
        self._providers[provider.name] = provider

    def get_provider(self, name: str = "auto") -> LLMProvider:
        """Get a provider by name, or auto-detect the first available one."""
        if name == "auto":
            for provider in self._providers.values():
                if provider.is_available():
                    return provider
            raise RuntimeError(
                "No LLM providers available. "
                "Set GROQ_API_KEY in .env to enable chat."
            )
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}. Available: {list(self._providers.keys())}")
        provider = self._providers[name]
        if not provider.is_available():
            raise RuntimeError(f"Provider '{name}' is not available. Check your API key or service.")
        return provider

    def get_available_providers(self) -> list:
        """List all registered providers with availability status."""
        return [
            {"name": p.name, "model": p.default_model, "available": p.is_available()}
            for p in self._providers.values()
        ]

    def get_models_catalog(self) -> dict:
        """Return full model catalog filtered to available providers.

        Returns dict of {model_id: model_info} for all models whose
        provider is registered and has a valid API key.
        """
        result = {}
        for provider in self._providers.values():
            if not provider.is_available():
                continue
            if provider.name == "ollama":
                # Ollama has dynamic models, add a single entry
                result[provider.default_model] = {
                    "provider": "ollama",
                    "label": provider.default_model,
                    "description": "Local model via Ollama",
                    "reasoning_param": None,
                }
            else:
                result.update(get_models_for_provider(provider.name))
        return result


def create_provider_registry() -> ProviderRegistry:
    """Create and populate the provider registry.

    Only Groq (Qwen3-32B) is registered for production use.
    Other providers are kept as commented-out fallbacks.
    """
    registry = ProviderRegistry()

    # Primary: Groq (open-source Qwen3-32B on LPU hardware)
    try:
        from llm.groq_provider import GroqProvider
        registry.register(GroqProvider())
    except ImportError:
        pass

    # Fallback providers (disabled for production — uncomment to re-enable)
    # try:
    #     from llm.openai_provider import OpenAIProvider
    #     registry.register(OpenAIProvider())
    # except ImportError:
    #     pass
    #
    # try:
    #     from llm.anthropic_provider import AnthropicProvider
    #     registry.register(AnthropicProvider())
    # except ImportError:
    #     pass
    #
    # try:
    #     from llm.google_provider import GoogleProvider
    #     registry.register(GoogleProvider())
    # except ImportError:
    #     pass
    #
    # try:
    #     from llm.ollama_provider import OllamaProvider
    #     from config import settings
    #     registry.register(OllamaProvider(
    #         base_url=settings.ollama_base_url,
    #         model=settings.ollama_model,
    #     ))
    # except ImportError:
    #     pass

    return registry

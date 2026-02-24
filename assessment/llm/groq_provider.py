"""Groq provider — OpenAI-compatible Chat Completions API on Groq LPU hardware."""
import os
import re
import time
from llm.base import LLMProvider, LLMResponse
from llm.models import get_model_info

DEFAULT_MODEL = "qwen/qwen3-32b"

# Strip Qwen3's <think>...</think> reasoning tags from responses
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


class GroqProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "groq"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODEL

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.environ.get("GROQ_API_KEY", ""),
            )
        return self._client

    def generate(self, system_prompt: str, messages: list,
                 model: str | None = None,
                 reasoning_config: dict | None = None) -> LLMResponse:
        client = self._get_client()
        model_id = model or DEFAULT_MODEL

        # Build standard Chat Completions messages
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        kwargs = {
            "model": model_id,
            "messages": api_messages,
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        start = time.perf_counter()
        resp = client.chat.completions.create(**kwargs)
        latency = (time.perf_counter() - start) * 1000

        text = resp.choices[0].message.content or ""
        # Strip Qwen3's <think> reasoning tags
        text = _THINK_RE.sub("", text).strip()

        input_tokens = None
        output_tokens = None
        if resp.usage:
            input_tokens = resp.usage.prompt_tokens
            output_tokens = resp.usage.completion_tokens

        return LLMResponse(
            text=text,
            provider="groq",
            model=model_id,
            latency_ms=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def is_available(self) -> bool:
        return bool(os.environ.get("GROQ_API_KEY"))

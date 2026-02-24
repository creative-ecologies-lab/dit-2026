import os
import time
from collections import defaultdict
from flask import Blueprint, render_template, request, jsonify, current_app
from llm.models import get_model_info
from usage_tracker import check_budget, record_usage

bp = Blueprint('chat', __name__, url_prefix='/chat')

# Simple in-memory rate limiter: max 30 messages per IP per hour
_RATE_LIMIT = 30
_RATE_WINDOW = 3600  # seconds
_rate_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str) -> bool:
    """Return True if under the rate limit."""
    now = time.time()
    cutoff = now - _RATE_WINDOW
    _rate_log[ip] = [t for t in _rate_log[ip] if t > cutoff]
    if len(_rate_log[ip]) >= _RATE_LIMIT:
        return False
    _rate_log[ip].append(now)
    return True


@bp.route('/')
def chat_page():
    providers = current_app.llm_registry.get_available_providers()
    available = [p for p in providers if p["available"]]
    # Auto-detect simple mode: single provider, or env override
    simple = (
        len(available) <= 1
        or os.environ.get("CHAT_SIMPLE_MODE", "").lower() in ("1", "true")
    )
    # In simple mode, resolve the display label for the fixed model
    model_label = None
    if simple and available:
        info = get_model_info(available[0]["model"])
        model_label = info["label"] if info else available[0]["model"]
    return render_template('chat.html', providers=providers,
                           simple_mode=simple, model_label=model_label)


@bp.route('/api/message', methods=['POST'])
def send_message():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
    if not _check_rate_limit(ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    data = request.get_json()
    user_message = data['message']
    provider_name = data.get('provider', 'auto')
    model_id = data.get('model')
    reasoning_value = data.get('reasoning')
    conversation_history = data.get('history', [])

    # Retrieve relevant context chunks
    chunks = current_app.search_engine.search(user_message, top_k=5)
    context = "\n\n---\n\n".join(
        f"[Source: {c.get('source_file','')}, Section: {c.get('section_title','')}]\n{c['text']}"
        for c in chunks
    )

    system_prompt = (
        "You are an expert on the Design in Tech Report 2026 E-P-I-A-S x SAE Framework "
        "by John Maeda for AI upskilling product designers. Answer questions based on the "
        "following framework content. Cite specific SAE levels and EPIAS stages when relevant. "
        "Be helpful and concrete in your advice.\n\n"
        f"FRAMEWORK CONTEXT:\n{context}"
    )

    # Build reasoning_config based on the model's parameter type
    reasoning_config = None
    if model_id and reasoning_value is not None:
        info = get_model_info(model_id)
        if info:
            param_type = info.get("reasoning_param")
            if param_type == "effort":
                reasoning_config = {"effort": reasoning_value}
            elif param_type == "thinking":
                reasoning_config = {"thinking": reasoning_value}
            elif param_type == "thinking_budget":
                reasoning_config = {"thinking_budget": reasoning_value}
            elif param_type == "thinking_level":
                reasoning_config = {"thinking_level": reasoning_value}

    # Check daily token budget before calling LLM
    if not check_budget():
        return jsonify({"error": "Daily token budget reached. Chat will resume tomorrow."}), 503

    provider = current_app.llm_registry.get_provider(provider_name)
    response = provider.generate(
        system_prompt=system_prompt,
        messages=conversation_history + [{"role": "user", "content": user_message}],
        model=model_id,
        reasoning_config=reasoning_config,
    )

    # Record token usage
    usage = record_usage(response.input_tokens or 0, response.output_tokens or 0)

    return jsonify({
        "response": response.text,
        "provider": response.provider,
        "model": response.model,
        "latency_ms": response.latency_ms,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "usage": usage,
        "sources": [{"file": c.get('source_file',''), "section": c.get('section_title','')} for c in chunks],
    })

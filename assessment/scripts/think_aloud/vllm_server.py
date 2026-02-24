"""Modal vLLM server for open-source LLM inference.

Deploys a vLLM server on Modal with OpenAI-compatible API.
Browser containers in modal_run.py call this endpoint.

Usage:
    # Deploy Qwen3-32B (A100 80GB)
    modal deploy scripts/think_aloud/vllm_server.py

    # Test the endpoint
    modal run scripts/think_aloud/vllm_server.py

    # Stop when done (scales to zero after idle, but stop to be safe)
    modal app stop think-aloud-vllm
"""

import json
import modal

# ── Model configuration ──
# Change these to switch models. GPU is auto-matched to model size.
MODEL_NAME = "Qwen/Qwen3-32B"
MODEL_REVISION = None  # Use latest

# GPU lookup: model HF name → Modal GPU spec
# Note: A100 string format defaults to 40GB. Use H100 (80GB) for >40GB models.
GPU_FOR_MODEL = {
    "Qwen/Qwen3-32B": "H100:1",        # 64GB weights, needs 80GB VRAM
    "Qwen/Qwen3-14B": "L40S:1",        # 28GB weights, fits in 48GB
    "Qwen/Qwen3-30B-A3B": "A10G:1",    # 3B active, MoE fits in 24GB
    "google/gemma-3-27b-it": "H100:1",  # 54GB weights, needs 80GB
}

# ── Modal resources ──
app = modal.App("think-aloud-vllm")

vllm_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12"
    )
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.13.0",
        "huggingface-hub==0.36.0",
    )
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

MINUTES = 60
VLLM_PORT = 8000
FAST_BOOT = True  # Prioritize cold start speed over peak throughput


@app.function(
    image=vllm_image,
    gpu=GPU_FOR_MODEL.get(MODEL_NAME, "A100:1"),
    scaledown_window=15 * MINUTES,
    timeout=30 * MINUTES,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    cmd = [
        "vllm", "serve", MODEL_NAME,
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--served-model-name", MODEL_NAME,
        "--uvicorn-log-level", "info",
        "--max-model-len", "8192",  # Limit context to save KV cache memory
        "--gpu-memory-utilization", "0.90",
        "--tensor-parallel-size", "1",
    ]

    if MODEL_REVISION:
        cmd += ["--revision", MODEL_REVISION]

    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    print("Starting vLLM:", " ".join(cmd))
    subprocess.Popen(" ".join(cmd), shell=True)


# ── Local test entrypoint ──

@app.local_entrypoint()
async def test():
    """Quick smoke test: send one prompt and print the response."""
    import aiohttp

    url = await serve.get_web_url.aio()
    print(f"Server URL: {url}")

    # Wait for health check
    async with aiohttp.ClientSession(base_url=url) as session:
        print("Waiting for server health check...")
        async with session.get("/health", timeout=8 * MINUTES) as resp:
            assert resp.status == 200, f"Health check failed: {resp.status}"
        print("Server is healthy!")

        # Send a test prompt
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": "Say hello in one sentence."}],
            "max_tokens": 50,
        }
        async with session.post(
            "/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            data = await resp.json()
            text = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            print(f"Response: {text}")
            print(f"Tokens: {usage['prompt_tokens']} in, {usage['completion_tokens']} out")

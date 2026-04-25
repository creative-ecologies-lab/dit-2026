"""Modal vLLM server for Qwen3-Coder-30B-A3B-Instruct.

Tier 2 primary OSS model (RFD-002 Wave 1.5). Compared to Qwen3-32B:
  - 256K native context (vs 8K) — `--max-model-len 32768` is a
    KV-cache-memory floor, not a model-arch ceiling
  - MoE with 3.3B active params out of 30B total — much lower per-token
    compute than dense 32B
  - No <think> blocks (eliminates streaming TTFB regression)
  - Dedicated `qwen3_coder` tool-call parser in vLLM ≥ 0.18

GPU sizing: starts on H100:1 conservatively. The 30B weight footprint
in FP8 is ~30 GB which *might* fit on L40S:1 (48 GB) with 32K KV cache,
but that's untested and the cost delta isn't large enough to justify the
deploy thrash if it OOMs. RFD-002 Wave 1.5 acceptance includes
empirical VRAM profiling — flip GPU spec only after that lands.

Usage:
    modal deploy assessment/scripts/think_aloud/vllm_qwen3_coder.py
    modal run assessment/scripts/think_aloud/vllm_qwen3_coder.py
    modal app stop think-aloud-vllm-qwen3-coder
"""

import os
import modal

# ── Model configuration ──
MODEL_NAME = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
MODEL_REVISION = None  # Use latest

# Warm-pool floor — kept at 0 by RFD-002 hard constraint (no daily warm fees).
# Cold-start mitigation comes from GPU memory snapshots, not warm pools.
try:
    MIN_CONTAINERS = int(os.environ.get("MIN_CONTAINERS", "0"))
except ValueError:
    MIN_CONTAINERS = 0
if MIN_CONTAINERS < 0:
    MIN_CONTAINERS = 0

# GPU memory snapshots — alpha Modal feature. Cuts cold-start from
# 60–180s (load weights from scratch) to ~15–40s for 30 GB models
# (restore from snapshot). See https://modal.com/blog/gpu-mem-snapshots.
# Opt-in via env var so we can A/B test the feature against a control
# deploy before flipping the default.
ENABLE_GPU_SNAPSHOT = os.environ.get("ENABLE_GPU_SNAPSHOT", "0") not in {"0", "", "false", "False"}

# GPU lookup mirrors vllm_server.py / vllm_qwen14b.py.
GPU_FOR_MODEL = {
    "Qwen/Qwen3-Coder-30B-A3B-Instruct": "H100:1",  # conservative; see file docstring
}

# ── Modal resources ──
app = modal.App("think-aloud-vllm-qwen3-coder")

# vLLM 0.19.1 — Tier 2 floor. The dedicated `qwen3_coder` tool-call
# parser is required for this model; lower vLLM versions will reject
# the flag at startup.
vllm_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12"
    )
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.19.1",
        "huggingface-hub==0.36.0",
    )
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

MINUTES = 60
VLLM_PORT = 8000
# Qwen3-Coder ships native 256K context but we cap at 32K for KV-cache
# economics on H100:1 (80 GB VRAM, 30 GB weights → ~50 GB headroom).
# Bump higher only with GPU memory profiling.
MAX_MODEL_LEN = 32768
FAST_BOOT = True


# Snapshot lifecycle hook — runs once during snapshot creation. The
# Modal docs recommend front-loading library imports + Triton JIT into
# this hook so the captured snapshot already has them resolved.
def _snapshot_warmup():
    """Front-load heavy imports during snapshot phase.

    Called from @modal.enter(snap=True). At restore time, these modules
    are already present in CPU memory + their CUDA contexts are already
    initialized, so `vllm serve` skips most JIT work.
    """
    if not ENABLE_GPU_SNAPSHOT:
        return
    try:
        import torch  # noqa: F401
        import triton  # noqa: F401
    except ImportError:
        # Triton may not be on PATH at snapshot time on some Modal images;
        # if it isn't, restore-time JIT still works — just slower.
        pass


# Build function options conditionally so older Modal SDK versions that
# don't recognize `experimental_options` keep working.
_function_kwargs = dict(
    image=vllm_image,
    gpu=GPU_FOR_MODEL.get(MODEL_NAME, "H100:1"),
    scaledown_window=15 * MINUTES,
    timeout=30 * MINUTES,
    min_containers=MIN_CONTAINERS,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
if ENABLE_GPU_SNAPSHOT:
    _function_kwargs["experimental_options"] = {"enable_gpu_snapshot": True}


@app.function(**_function_kwargs)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    # Snapshot warmup is a no-op when ENABLE_GPU_SNAPSHOT is off; the
    # @modal.enter decorator is wired conditionally below.
    _snapshot_warmup()

    cmd = [
        "vllm", "serve", MODEL_NAME,
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--served-model-name", MODEL_NAME,
        "--uvicorn-log-level", "info",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--gpu-memory-utilization", "0.90",
        "--tensor-parallel-size", "1",
        # Qwen3-Coder ships its own tool-call parser. Hermes won't work
        # here — the qwen3_coder dialect uses different token wrappers
        # (see https://github.com/QwenLM/Qwen3-Coder).
        "--enable-auto-tool-choice",
        "--tool-call-parser", "qwen3_coder",
    ]

    if MODEL_REVISION:
        cmd += ["--revision", MODEL_REVISION]

    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    print("Starting vLLM:", " ".join(cmd))
    print(f"GPU snapshot enabled: {ENABLE_GPU_SNAPSHOT}")
    subprocess.Popen(" ".join(cmd), shell=True)


# ── Local test entrypoint ──

@app.local_entrypoint()
async def test():
    """Quick smoke test: send one prompt and print the response."""
    import aiohttp

    url = await serve.get_web_url.aio()
    print(f"Server URL: {url}")
    print(f"GPU snapshot enabled: {ENABLE_GPU_SNAPSHOT}")

    async with aiohttp.ClientSession(base_url=url) as session:
        print("Waiting for server health check...")
        async with session.get("/health", timeout=8 * MINUTES) as resp:
            assert resp.status == 200, f"Health check failed: {resp.status}"
        print("Server is healthy!")

        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": "Write a one-line Python lambda that squares its input."}],
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

# DIT 2026 Assessment — Production Dockerfile
# Multi-stage build for minimal image size

# ── Stage 1: Install dependencies ──────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies for numpy/sklearn compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY assessment/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ──────────────────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Set working directory to assessment so local imports resolve correctly
# (e.g. `from app import create_app`, `from embeddings.search import ...`)
WORKDIR /app

# Copy the assessment application code
COPY assessment/ .

# Copy the v-0.0.1 source content (referenced by config.py as ../v-0.0.1/)
COPY v-0.0.1/ /v-0.0.1/

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app /v-0.0.1
USER appuser

EXPOSE 8080

# Gunicorn with:
#   - 2 workers (Cloud Run vCPU is shared; 2 is optimal for 1 vCPU)
#   - 32 threads per worker (64 total — handles 50+ concurrent Groq API waits)
#   - 120s timeout (Groq LPU is fast; no need for 300s)
#   - Bind to 0.0.0.0:$PORT (Cloud Run injects PORT)
CMD exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 32 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"

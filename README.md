# Design in Tech Report 2026 by @johnmaeda

NEW: Try out the simple mapper https://johnmaeda.github.io/dit26-ai-upskilling-gameboard/

---

> "From UX to AX"

> MAR 18, 2026 | 11:30AM – 12:30PM CT

> AUSTIN MARRIOTT DOWNTOWN - WALLER BALLROOM C

Full details are [here](https://schedule.sxsw.com/2026/events/PP1148536).

![](assets/sxsw.gif)

---

## Interactive Assessment App

The `assessment/` directory contains a Flask web app that lets product designers self-assess their position on the E-P-I-A-S x SAE Framework.

### Features

- **Self-Assessment Quiz** — 11 questions to find your SAE automation level (L0-L5) and E-P-I-A-S maturity stage. No API key required.
- **RAG-Powered Chat** — Ask questions about the framework. Semantic search over the full report content, powered by your choice of LLM (OpenAI, Anthropic, Google, or local Ollama).
- **Framework Reader** — Read John Maeda's original, unedited framework text directly in the browser.
- **Interactive Matrix** — Visualize your placement on the 6x5 E-P-I-A-S x SAE grid with personalized growth paths.

### Quick Start

```bash
cd assessment
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python __main__.py
```

The app starts at `http://localhost:5002`. The self-assessment and framework reader work without any API keys.

To enable the RAG chat, add keys to the Settings page in the browser, or create an `assessment/.env` file:

```
OPENAI_API_KEY=sk-...
# and/or
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

### Syncing with Upstream

The assessment app reads content directly from `v-0.0.1/` — when the upstream framework text is updated, the app automatically uses the new content. To pull the latest:

```bash
git fetch upstream
git merge upstream/main
```

After content updates, regenerate embeddings for the chat feature:

```bash
cd assessment
python scripts/generate_embeddings.py   # requires OPENAI_API_KEY
```
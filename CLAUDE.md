# Project instructions for Claude

> This file is the per-repo hook. Global norms (worktree workflow, backlog
> tracking, secret handling, git safety, Anthropic-SDK conventions) live in
> `~/.claude/CLAUDE.md` and the project memory under
> `~/.claude/projects/<slug>/memory/MEMORY.md`. Read those first.

## What this repo is

The "AI Skills Map" / DIT Assessment 2026 app — a Flask web app that guides
users through a design-in-tech framework self-assessment and visualizes the
result as a Maeda tree. Content lives in `assessment/` and `v-0.0.1/`.

Live at **https://aiskillsmap.noahratzan.com**.

## Where to start

- Entry point: `app.py` (Flask) — launched under gunicorn in production
- Key docs: `DEPLOYMENT_PLAN.md`, `README.md`, framework content in
  `assessment/` and `v-0.0.1/`
- Tests: `tests/` if present; otherwise manual QA
- Deploy: Cloud Run service **`dit-maeda`** in GCP project `mmx-475801`
  (the old `dit-assessment` service also exists but only `dit-maeda` has the
  custom domain)

## Commands

| Purpose | Command |
|---|---|
| install | `pip install -r requirements.txt` |
| dev | `python app.py` (or `flask run`) |
| test | `pytest` (if test suite wired up) |
| build / deploy | `gcloud run deploy dit-maeda --source . --region us-central1 --allow-unauthenticated --project mmx-475801` |

Production runtime: **gunicorn, 2 workers, 32 threads per worker**. Do not
change worker/thread counts without checking `DEPLOYMENT_PLAN.md`.

## Agent / ledger integration (ach)

This repo is registered with `agent-control-hub` (the `ach` CLI). Sessions,
costs, and commits flow into the ledger at `~/.ach/ops.db`.

- Register: `ach repo list` should show this repo.
- Commit hook: `.git/hooks/post-commit` emits `CommitLinked` events automatically.
- Manual emit: `ops emit CapabilityInvoked --payload '{"capability":"…"}'`.

### Project-specific ach notes

- **Primary clone is currently on a feature branch**
  (`chore/dependency-audit-march-2026`) with recent dependency-audit commits
  **unmerged to `main`**. When onboarding tooling lands on a feature branch,
  that's fine — Noah merges to default separately.
- **No GitHub Actions CI/CD.** Deploys are manual, source-based, Dockerfile
  at repo root.
- **Modal think-aloud standard model: Qwen3-32B** (post-ARIA v2.1). User
  directive: use ONLY Qwen for think-aloud runs, not Haiku. See
  `assessment/scripts/think_aloud/`.
- **Modal vLLM app**: `ach-vllm-qwen3-32b` on H100:1 (renamed from
  `think-aloud-vllm` on 2026-04-30 — see agent-control-hub PR
  `feat/vllm-app-rename`). URL
  `https://noah-ratzan--ach-vllm-qwen3-32b-serve.modal.run`, scales to
  zero after 15 min idle, cold start ~60-90s. Shared by dit-2026
  think-aloud AND `ach` (qwen-modal preset in
  `~/.ach/config/models.yaml`). The vLLM template lives in
  `agent-control-hub/scripts/modal/vllm_server.py` (canonical) — the
  former mirrors at `assessment/scripts/think_aloud/vllm_*.py` were
  deleted after the relocation. Redeploy from the agent-control-hub
  worktree: `bash scripts/deploy_modal_vllm.sh`.
- Ledger project-id: `dit-2026`.

## Conventions specific to this repo

- Framework content is versioned (`v-0.0.1/`). Do not edit past-version content
  — add a new version directory if the framework evolves.
- The forest visualization replaces the earlier heatmap — see project memory
  (`project_forest_vision.md`, `project_forest_heatmap.md`) for context.

## Do-not-touch list

- `v-0.0.1/` — frozen framework content
- GCP project string `mmx-475801` — do not change to `creative-eco-lab`
  (that project doesn't exist)

# Engineering Workflow

This repository keeps the course notebook-first while applying production-style guardrails.

## Daily Commands

```bash
mise install
mise run setup
mise run verify
```

Single checks:

```bash
mise run lint
mise run typecheck
mise run test
mise run notebooks:check
```

Notebook work:

```bash
uv run jupyter lab
```

## What each task does

- `setup`: syncs locked Python dependencies via `uv sync --frozen --group dev`
- `lint`: runs `ruff` on `src/`, `tests/`, and `scripts/`
- `typecheck`: runs `pyright` on typed Python code
- `test`: runs deterministic unit tests (no external APIs)
- `notebooks:check`: verifies notebook JSON validity and expected imports from `src/`
- `verify`: runs all checks above

## Troubleshooting

- If `mise` refuses local config, run `mise trust` from repo root once.
- If lockfile and env differ, run `uv sync --group dev` and then `mise run verify`.
- If notebook imports fail, ensure `mise run setup` succeeded and `uv.lock` is present.

## Out of scope for default verification

The default `verify` path intentionally avoids:

- GPU execution
- model downloads / gated Hugging Face artifacts
- external API calls

Use `uv sync --group heavy` for optional local torch-based workflows, then follow Module 6 instructions plus upstream `model_swarm` guidance for heavyweight experiments.

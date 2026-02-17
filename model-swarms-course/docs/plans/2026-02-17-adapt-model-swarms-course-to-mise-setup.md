# Adapt Model Swarms Course To My Setup (Instructions For Another Model)

Use this document as your execution brief.

## 1) Local Reality You Must Respect

- Workspace: `/Users/joe/Code/code-research/model-swarms-course`
- Existing course assets: notebook-only curriculum (`module_01_...ipynb` through `module_08_...ipynb` plus `exercises.ipynb`)
- Current setup from `README.md`: course still suggests `pip` + `conda` + manual steps
- Active toolchain from `mise current` on this machine:
  - `pixi 0.63.2`
  - `uv 0.10.2`
  - `ruff 0.15.1`
  - `npm:pyright 1.1.408`
  - plus CLI tooling (`rg`, `fd`, `bat`, etc.)
- `mise` source of truth today: `~/.config/mise/config.toml` (global tools); there is no project-local `.mise.toml` yet.

Do not propose a conda-first workflow. Adapt this course to `mise` + `uv` (and optionally `pixi` where useful), with reproducibility and engineering rigor.

## 2) Goal

Transform this notebook course into a reproducible, engineering-grade learning project that still feels interactive, but behaves like production-quality research software.

## 3) Deliverables You Must Produce

Create or update these artifacts in this repo:

1. `.mise.toml`
2. `pyproject.toml`
3. `uv.lock` (generated)
4. `src/model_swarms_course/` package for shared notebook logic
5. `tests/` with fast, deterministic tests for non-GPU core logic
6. Notebook quality config (`.ruff.toml` or `pyproject` sections, optional `nbqa`/`nbval` config)
7. `README.md` updates replacing conda setup with `mise` + `uv` workflow
8. `docs/engineering-workflow.md` describing dev/test/lint/run flow

If a file already exists, modify it instead of duplicating.

## 4) Quality Bar (Non-Negotiable)

- Reproducible environment bootstrap from a clean machine in <= 10 minutes (excluding large model downloads)
- One-command setup, one-command verify
- Deterministic tests that do not require external API calls or paid services
- Type checks and lint checks wired into normal workflow
- Notebooks remain executable end-to-end, but reusable code moves into `src/`

## 5) Design Constraints

- Prefer `uv` for Python dependency and lock management.
- Use project-local `mise` tasks as developer entrypoints.
- Keep GPU/model-heavy steps optional and explicitly separated from default CI/dev checks.
- Do not break pedagogical flow of modules.
- Keep the dependency footprint minimal (YAGNI).

## 6) Implementation Plan You Should Execute

### Phase A: Environment Foundation

1. Add project-local `.mise.toml`:
   - Pin Python runtime.
   - Define tasks:
     - `setup`
     - `lint`
     - `typecheck`
     - `test`
     - `verify`
     - `notebooks:check` (can be lightweight)
2. Initialize `pyproject.toml` for package + tooling config.
3. Add core deps and dev deps with `uv`, then generate `uv.lock`.

### Phase B: Engineering Structure

1. Create `src/model_swarms_course/` and move reusable notebook code there.
2. Add tests for:
   - Swarm/PSO helper logic
   - Weight merge utilities (small tensor fixtures)
   - Data/preprocessing helpers
3. Ensure notebooks import from `src/model_swarms_course` instead of duplicating logic.

### Phase C: Verification & Notebook Guardrails

1. Wire `ruff` and `pyright`.
2. Add a lightweight notebook execution/check path (for example: selected smoke cells or `nbval` subset).
3. Make `mise run verify` execute all default quality gates in sequence.

### Phase D: Documentation

1. Replace README setup section with `mise` + `uv` commands.
2. Add an explicit “heavy experiment path” section for optional model downloads, HF auth, and GPU runs.
3. Add `docs/engineering-workflow.md` with:
   - Daily commands
   - Troubleshooting
   - What is intentionally out of scope for default verification

## 7) Command Interface Expectations

Your final setup should support this shape:

```bash
mise install
mise run setup
mise run verify
```

And individually:

```bash
mise run lint
mise run typecheck
mise run test
mise run notebooks:check
```

## 8) Acceptance Criteria Checklist

- [ ] Fresh clone works with `mise install && mise run setup`
- [ ] `mise run verify` passes locally without GPU
- [ ] README no longer requires conda
- [ ] Shared logic extracted from notebooks into `src/`
- [ ] Tests exist and validate core algorithmic pieces
- [ ] Notebook checks are present and documented
- [ ] Workflow docs are clear enough for a new contributor

## 9) Output Format Required From You

When done, report:

1. Files created/modified (with one-line purpose each)
2. Exact commands run
3. Verification results
4. Known limitations and explicit follow-up tasks

If any requirement above is not met, say so directly and explain why.

---
name: playground
description: Use when creating a standalone HTML report, interactive explainer, diagram, code or design review, slide deck, research page, or browser-based editor for this repository.
---

# Playground

Create self-contained static HTML artifacts that can be committed on a research branch and published with GitHub Pages. Use the pristine gallery in `examples/` as the visual source of truth.

## Page contract

For every generated page:

1. Read `references/anthropic-style.md`.
2. Inspect `examples/index.html` or `examples/README.md`, then read 1-3 relevant numbered examples in full.
3. Name the composition, hierarchy, controls, or visual patterns borrowed from each example before writing.
4. Use the user's real evidence and content. Never copy sample data.
5. Render dark on first visit and first paint.
6. Put a clearly labeled theme toggle in the primary header or toolbar. Persist an explicit choice and default to dark when none exists.
7. Keep the artifact self-contained unless the task explicitly requires an asset bundle. Use relative paths for every local asset.
8. Make the result work at phone and desktop widths with keyboard-visible controls and no horizontal overflow.
9. Add interaction only when it improves understanding, review, choice, or reuse. Interactive pages end with a useful copy or export surface.

## Choose the mode

| User intent | Start with |
| --- | --- |
| Compare approaches | `examples/01`, `examples/02` |
| Code review or PR writeup | `examples/03`, `examples/04`, `examples/17` |
| Design system exploration | `examples/05`, `examples/06` |
| Prototype behavior | `examples/07`, `examples/08` |
| Slides or deck | `examples/09-slide-deck.html` plus topic examples |
| Diagram or SVG illustration | `examples/10`, `examples/13` |
| Status, incident, or decision report | `examples/11`, `examples/12` |
| Research or concept explainer | `examples/14`, `examples/15` |
| Implementation plan | `examples/16-implementation-plan.html` |
| Triage, settings, or prompt editor | `examples/18` through `examples/20` |

Use `examples/index.html` when the mode is unclear. A page may combine patterns from several examples.

## Behavioral templates

Read a matching file under `templates/` when the artifact needs structured interaction:

- `design-playground.md` for component, spacing, color, typography, animation, or responsive choices;
- `data-explorer.md` for SQL, APIs, pipelines, regex, cron, or structured configuration;
- `concept-map.md` for learning maps, scope maps, dependency maps, or knowledge gaps;
- `document-critique.md` for approve, reject, and comment review flows;
- `diff-review.md` for clickable code comments and copyable review output;
- `code-map.md` for architecture nodes, filters, comments, and copy-back context.

Templates define behavior, not appearance. Style the result from the selected numbered examples.

## Build workflow

1. **Gather evidence.** Read the source material, code, diffs, data, or report needed to make every claim inspectable.
2. **Choose the primary surface.** Put the answer, comparison, diagram, metrics, live preview, or editor before supporting detail.
3. **Build the publishing artifact.** Write the final GitHub Pages entry point to `index.html` at the repository root. Put optional static files under `assets/` and reference them relatively. Do not reference files under `.agents/` from the final page.
4. **Apply the visual contract.** Use semantic HTML, real tables, inline SVG where useful, and the dark-first tokens and toggle from `references/anthropic-style.md`.
5. **Add bounded interaction.** Keep one state object, make selected state visible and accessible, and provide useful copy or export output.
6. **Keep publication static.** Do not require server-side code, private services, credentials, or local-only paths. Avoid remote CDNs unless the user explicitly accepts that dependency.
7. **Validate locally.** From the repository root run:

   ```bash
   bash .agents/skills/playground/scripts/serve-page.sh index.html
   ```

   The script serves only on `127.0.0.1` and prints the local URL. Stop it with:

   ```bash
   bash .agents/skills/playground/scripts/serve-page.sh --stop
   ```

8. **Inspect in a browser.** When Chromium or Playwright is available, check desktop and phone viewports, both themes, keyboard focus, interactions, console output, and local asset requests. Do not install browser tooling unless the task or environment permits it.
9. **Prepare the handoff.** Report the local path, checks performed, and any limits. State that GitHub Pages becomes available only after the branch is pushed and selected or deployed in repository Pages settings.

## GitHub Pages contract

A final report branch contains a root `index.html`. The repository owner can publish it from **Settings -> Pages -> Deploy from a branch**, selecting the task branch and `/ (root)`. The project URL is:

```text
https://joehelbing.github.io/code-research/
```

GitHub Pages is public and this repository has one active Pages site. Switching the source branch replaces the currently published experiment. Never claim the page is live without verifying the deployed URL.

## Quality gate

Before delivery, confirm:

- the selected examples were read and the borrowed patterns are identifiable;
- first visit and first paint are dark;
- the labeled theme toggle is visible, works in both directions, and persists;
- the answer or primary result appears before supporting detail;
- code, command, chart, badge, and disabled-control contrast works in both themes;
- interactive state is visible and copy or export output is useful;
- the page works at desktop and phone widths without horizontal overflow;
- focus is visible, controls have accessible names, and reduced motion is respected;
- local assets load with relative URLs and no secrets or local filesystem paths appear;
- source and user-controlled strings use `textContent`, text nodes, or equivalent escaping rather than unsafe `innerHTML` interpolation;
- the browser console has no errors.

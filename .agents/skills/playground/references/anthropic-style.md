# Anthropic HTML Style Contract

Use this reference for every page created by the playground skill. The pristine
files in `../examples/` are the visual source of truth. This document adds the
repository requirements the gallery does not provide: every generated page is
dark-first, has a prominent theme toggle, and works as a static GitHub Pages
artifact.

## Start From Examples

Before writing HTML:

1. Open `../examples/index.html` or its README to choose the artifact family.
2. Read 1-3 numbered examples in full.
3. Name the concrete patterns being borrowed: page composition, hierarchy,
   typography, palette roles, controls, navigation, data display, or export.
4. Build with the user's real content. Never copy Acme sample data or merely
   recolor an example.

Use the examples by intent:

| Intent | Examples |
| --- | --- |
| Explore or compare approaches | `01`, `02` |
| Review or explain code | `03`, `04`, `17` |
| Design systems and component choices | `05`, `06` |
| Prototype behavior or animation | `07`, `08` |
| Slide deck | `09` |
| SVG illustration or diagram | `10`, `13` |
| Status, incident, or decision report | `11`, `12` |
| Research or concept explanation | `14`, `15` |
| Implementation plan | `16` |
| Interactive editor or decision surface | `18`, `19`, `20` |

Combine examples when the artifact spans purposes. A decision report might use
`11` for summary hierarchy, `14` for inspectable evidence, and `20` for a
copyable decision output.

## Visual Grammar

Preserve the gallery's shared visual language while adapting it to the content:

- editorial, product-like composition rather than decorated documentation;
- serif display type, restrained sans-serif body type, and monospace labels;
- warm neutrals with clay, oat, olive, and rust used by semantic role;
- thin borders, modest radii, compact controls, and quiet surfaces;
- one strong hierarchy: answer first, evidence next, details last;
- bespoke layouts chosen for the information, not a uniform card grid;
- visible controls with immediate feedback;
- restrained motion that explains change rather than decorating the page.

Use the selected examples to decide proportions and composition. This reference
is not a substitute for reading them.

## Static GitHub Pages Boundary

The final publishing entry point is the repository-root `index.html`. Keep it
portable and static:

- use relative links such as `./assets/figure.svg`, never absolute filesystem
  paths, `file://` URLs, or root-relative site paths such as `/assets/...`;
- keep CSS and JavaScript inline by default; place larger original assets under
  `assets/` only when that improves maintainability;
- avoid CDNs, remote fonts, analytics, API calls, and third-party embeds unless
  the user explicitly accepts the availability and privacy trade-off;
- do not include credentials, private service URLs, unpublished source, or
  content that cannot be public;
- make navigation and asset loading work under the project path
  `https://joehelbing.github.io/code-research/`, not only at a domain root;
- use feature detection and a readable fallback when a browser API is optional.

GitHub Pages serves static files only. A local preview server is a validation
tool, not a runtime dependency.

## Mandatory Dark-First Theme

Every generated page must:

- render dark on the first visit and first paint;
- put a clearly labeled theme toggle in the primary page header or top toolbar;
- keep the toggle visible at desktop and narrow widths;
- let the user switch between dark and light modes;
- persist an explicit user choice in `localStorage`;
- use dark when no valid saved choice exists;
- update the button label and accessible state when the theme changes.

The control is first-class page UI. Do not hide it in a menu, make it icon-only,
or rely only on `prefers-color-scheme`. A returning user's saved choice may
supersede the dark default.

### Document and pre-paint initialization

Start the document in dark mode and initialize the saved choice before CSS can
paint the page:

```html
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <script>
    (() => {
      let theme = "dark";
      try {
        const saved = localStorage.getItem("playground-theme");
        if (saved === "light" || saved === "dark") theme = saved;
      } catch (_) {}
      document.documentElement.dataset.theme = theme;
    })();
  </script>
```

Do not initialize from the operating-system preference. The product default is
dark.

### Semantic theme tokens

Use semantic roles so all surfaces switch together. These values adapt the
gallery's warm ivory/slate/clay/oat/olive language rather than introducing a
separate visual system:

```css
:root,
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #141413;
  --surface: #1d1d1a;
  --surface-raised: #25241f;
  --text: #f5f1e8;
  --text-muted: #aaa69d;
  --border: #3b3932;
  --clay: #e58a6b;
  --clay-strong: #f09a79;
  --oat: #c8b99f;
  --olive: #a7b98a;
  --rust: #df766b;
  --code-bg: #0d0d0c;
  --code-text: #f5f1e8;
  --focus: #f0a07f;
}

:root[data-theme="light"] {
  color-scheme: light;
  --bg: #faf9f5;
  --surface: #ffffff;
  --surface-raised: #f0eee6;
  --text: #141413;
  --text-muted: #6f6d66;
  --border: #d1cfc5;
  --clay: #d97757;
  --clay-strong: #b85c3e;
  --oat: #e3dacc;
  --olive: #788c5d;
  --rust: #b04a3f;
  --code-bg: #1b1b19;
  --code-text: #faf9f5;
  --focus: #b85c3e;
}

html { background: var(--bg); }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
}
```

Add transitions only after the initial paint so loading a saved theme does not
flash or animate:

```css
body.theme-ready,
body.theme-ready * {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-duration: 160ms;
  transition-timing-function: ease;
}

@media (prefers-reduced-motion: reduce) {
  body.theme-ready,
  body.theme-ready * { transition-duration: 0ms; }
}
```

Keep foreground/background pairs explicit for code, commands, charts, and badges.
Do not derive an inverted surface from a token whose role reverses between
modes.

### First-class toggle markup

Place the control alongside the title, metadata, or primary actions:

```html
<header class="page-header">
  <div>
    <p class="eyebrow">Research report</p>
    <h1>Page title</h1>
  </div>
  <button class="theme-toggle" id="theme-toggle" type="button"
          aria-pressed="false">
    <span class="theme-toggle__indicator" aria-hidden="true"></span>
    <span class="theme-toggle__label">Light mode</span>
  </button>
</header>
```

Use a text label, not only a sun or moon glyph. Keep a 44px minimum hit target
and a visible focus ring:

```css
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.theme-toggle {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 9px 13px;
  color: var(--text);
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: 999px;
  font: 600 12px/1 ui-monospace, "SFMono-Regular", Consolas, monospace;
  cursor: pointer;
}

.theme-toggle__indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--clay);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--clay) 18%, transparent);
}

.theme-toggle:hover { border-color: var(--clay); }
.theme-toggle:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 45%, transparent);
  outline-offset: 3px;
}
```

### Toggle behavior

Run this after the button markup:

```html
<script>
  (() => {
    const root = document.documentElement;
    const button = document.getElementById("theme-toggle");
    if (!button) return;

    const label = button.querySelector(".theme-toggle__label");

    function renderTheme(theme) {
      const isLight = theme === "light";
      root.dataset.theme = isLight ? "light" : "dark";
      button.setAttribute("aria-pressed", String(isLight));
      button.setAttribute(
        "aria-label",
        isLight ? "Switch to dark mode" : "Switch to light mode"
      );
      if (label) label.textContent = isLight ? "Dark mode" : "Light mode";
    }

    renderTheme(root.dataset.theme === "light" ? "light" : "dark");
    document.body.classList.add("theme-ready");

    button.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      renderTheme(next);
      try { localStorage.setItem("playground-theme", next); } catch (_) {}
    });
  })();
</script>
```

## Page Composition Contract

Every page should expose:

1. **Immediate answer:** title, one-sentence framing, and the result or decision.
2. **Primary evidence surface:** the main comparison, diagram, metrics, editor,
   or explanation visible without hunting.
3. **Inspectable detail:** sources, file paths, calculations, caveats, and
   secondary evidence grouped below or in disclosure controls.
4. **Action surface:** copy, export, selection summary, navigation, or next step
   when the artifact is interactive or decision-oriented.

Use `<details>` for secondary material, real `<table>` markup for tabular data,
and inline SVG for bespoke diagrams. Follow examples `10` and `13` for SVG
composition and labels.

## Interaction Contract

For interactive artifacts:

- keep one state object;
- update the result immediately after each control change;
- use sensible defaults and a small number of meaningful presets;
- make selected state visible in text and through `aria-pressed`, native inputs,
  or equivalent semantics;
- include a copyable prompt, Markdown, JSON, YAML, CSS, or decision summary;
- insert source and user-controlled strings with `textContent`, text nodes, or
  equivalent escaping; never pass untrusted values through `innerHTML`;
- confirm copy actions without blocking the workflow.

The theme toggle remains independent from artifact state and is present even
when the page has other dense controls.

## Responsive and Accessibility Checks

Before delivery, verify:

- the first paint is dark with no light flash;
- the toggle is visible and usable at desktop and narrow widths;
- the saved light choice survives reload and can switch back to dark;
- text, code, charts, badges, and disabled controls have readable contrast in
  both modes;
- keyboard focus is visible and all controls have accessible names;
- grids and flex children shrink without horizontal overflow;
- motion respects `prefers-reduced-motion`;
- hostile-looking source text such as `<img src=x onerror=alert(1)>` renders as
  text rather than markup;
- the page has no console errors.

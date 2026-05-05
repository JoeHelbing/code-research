# visual-explainer (skill)

A standalone Claude Code skill bundle, repackaged from the upstream
[`nicobailon/visual-explainer`](https://github.com/nicobailon/visual-explainer)
plugin. It generates self-contained HTML pages — diagrams, diff reviews, plan
reviews, slide decks, data tables — instead of falling back to ASCII art.

This is a plain skill: a `SKILL.md` plus `references/`, `templates/`,
`scripts/`, and `commands/` (prompt templates the skill reads). No plugin
manifest, no marketplace metadata.

## Install

Unzip into your Claude Code skills directory:

```bash
# User-level (available in every project)
unzip visual-explainer.zip -d ~/.claude/skills/

# Or project-level (checked in alongside the repo)
unzip visual-explainer.zip -d .claude/skills/
```

The skill auto-loads when its description matches the request — diagrams,
architecture overviews, diff reviews, plan reviews, project recaps, comparison
tables, slide decks, etc.

## Layout

```
visual-explainer/
├── SKILL.md              ← workflow + design principles (entry point)
├── commands/             ← prompt templates per workflow
├── references/           ← CSS patterns, libraries, slide patterns, nav
├── templates/            ← reference HTML templates
└── scripts/share.sh      ← optional Vercel-deploy helper
```

## Output

Generated pages land in `~/.agent/diagrams/<name>.html` and are opened in the
browser. Self-contained — only CDN links for fonts and optional libraries.

## License

MIT — see upstream repo.

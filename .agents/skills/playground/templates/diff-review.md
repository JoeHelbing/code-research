# Diff Review Template

Use this template when the playground is about reviewing code diffs: git commits, pull requests, code changes with interactive line-by-line commenting for feedback.

This template defines review behavior and data shape only. Read
`../references/anthropic-style.md`, select relevant files from `../examples/`,
and derive every color, surface, type treatment, and control style from them.
The generated page still starts dark and exposes the mandatory theme toggle.

## Layout

```
+-------------------+----------------------------------+
|                   |                                  |
|  Commit Header:   |  Diff Content                    |
|  • Hash           |  (files with hunks)              |
|  • Message        |  with line numbers               |
|  • Author/Date    |  and +/- indicators              |
|                   |                                  |
+-------------------+----------------------------------+
|  Prompt Output Panel (fixed bottom-right)            |
|  [ Copy All ]                                        |
|  Shows all comments formatted for prompt             |
+------------------------------------------------------+
```

Diff review playgrounds display git diffs with syntax highlighting. Users click lines to add comments, which become part of the generated prompt for code review feedback.

## Control types for diff review

| Feature | Control | Behavior |
|---|---|---|
| Line commenting | Click any diff line | Opens textarea below the line |
| Comment indicator | Badge on commented lines | Shows which lines have feedback |
| Save/Cancel | Buttons in comment box | Persist or discard comment |
| Copy prompt | Button in prompt panel | Copies all comments to clipboard |

## Diff rendering

Parse diff data into structured format for rendering:

```javascript
const diffData = [
  {
    file: "path/to/file.py",
    hunks: [
      {
        header: "@@ -41,13 +41,13 @@ function context",
        lines: [
          { type: "context", oldNum: 41, newNum: 41, content: "unchanged line" },
          { type: "deletion", oldNum: 42, newNum: null, content: "removed line" },
          { type: "addition", oldNum: null, newNum: 42, content: "added line" },
        ]
      }
    ]
  }
];
```

## Line type treatment

Use semantic tokens whose dark and light values come from the selected examples
and `anthropic-style.md`. Preserve the conventional prefixes so status never
depends on color alone.

| Type | Background token | Text token | Prefix |
| --- | --- | --- | --- |
| `context` | transparent | `--text` | ` ` (space) |
| `addition` | `--diff-add-bg` | `--diff-add-text` | `+` |
| `deletion` | `--diff-delete-bg` | `--diff-delete-text` | `-` |
| `hunk-header` | `--diff-hunk-bg` | `--diff-hunk-text` | `@@` |

## Comment system

Each diff line gets a unique identifier for comment tracking:

```javascript
const comments = {}; // { lineId: commentText }

function selectLine(lineId, lineEl) {
  // Deselect previous
  document.querySelectorAll('.diff-line.selected').forEach(el =>
    el.classList.remove('selected'));
  document.querySelectorAll('.comment-box.active').forEach(el =>
    el.classList.remove('active'));

  // Select new
  lineEl.classList.add('selected');
  document.getElementById(`comment-box-${lineId}`).classList.add('active');
}

function saveComment(lineId) {
  const textarea = document.getElementById(`textarea-${lineId}`);
  const comment = textarea.value.trim();

  if (comment) {
    comments[lineId] = comment;
  } else {
    delete comments[lineId];
  }

  renderDiff(); // Re-render to show comment indicator
  updatePromptOutput();
}
```

## Prompt output format

Generate a structured code review format:

```javascript
function updatePromptOutput() {
  const commentKeys = Object.keys(comments);

  if (commentKeys.length === 0) {
    promptContent.innerHTML = '<span class="no-comments">Click on any line to add a comment...</span>';
    return;
  }

  let output = 'Code Review Comments:\n\n';

  commentKeys.forEach(lineId => {
    const lineEl = document.querySelector(`[data-line-id="${lineId}"]`);
    const file = lineEl.dataset.file;
    const lineNum = lineEl.dataset.lineNum;
    const content = lineEl.dataset.content;

    output += `At ${file}:${lineNum}\n`;
    output += `   Code: ${content.trim()}\n`;
    output += `   Comment: ${comments[lineId]}\n\n`;
  });

  promptContent.textContent = output;
}
```

## Data attributes for line elements

Store metadata on each line element for prompt generation:

```html
<div class="diff-line addition"
     data-line-id="0-1-5"
     data-file="src/utils/handler.py"
     data-line-num="45"
     data-content="subagent_id = tracker.register()">
```

## Pre-populating with real data

To create a diff viewer for a specific commit:

1. Run `git show <commit> --format="%H%n%s%n%an%n%ad" -p`
2. Parse the output into the `diffData` structure
3. Include commit metadata in the header section

## Theme integration

Use the mandatory dark-first initialization and header toggle from
`../references/anthropic-style.md`. Define diff-specific semantic tokens in both
theme blocks, using the selected examples to choose their values:

```css
.file-card {
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
}
.diff-line.addition {
  color: var(--diff-add-text);
  background: var(--diff-add-bg);
}
.diff-line.deletion {
  color: var(--diff-delete-text);
  background: var(--diff-delete-bg);
}
```

## Interactive features

- **Hover hint:** Show "Click to comment" tooltip on line hover
- **Comment indicator:** Text or dot badge on lines with saved comments
- **Toast notification:** "Copied to clipboard!" feedback on copy
- **Edit existing:** Allow editing previously saved comments

## Example topics

- Git commit review (single commit diff with line comments)
- Pull request review (multiple commits, file-level and line-level comments)
- Code diff comparison (before/after refactoring)
- Merge conflict resolution (showing both versions with annotations)
- Code audit (security review with findings per line)

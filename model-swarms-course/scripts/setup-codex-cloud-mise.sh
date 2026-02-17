#!/usr/bin/env bash
set -euo pipefail

# Codex Cloud bootstrap that mirrors Joe's global mise toolset.

MISE_BIN="${MISE_BIN:-$HOME/.local/bin/mise}"
TOOLS=(
  "pixi"
  "uv"
  "zoxide"
  "eza"
  "bat"
  "ripgrep"
  "fd"
  "fzf"
  "atuin"
  "shellcheck"
  "tlrc"
  "ruff"
  "ast-grep"
  "chezmoi"
  "pipx:llm"
  "npm:pyright"
  "pipx:zuban"
)

log() {
  printf "\n[%s] %s\n" "$(date +'%H:%M:%S')" "$*"
}

ensure_mise() {
  if command -v mise >/dev/null 2>&1; then
    MISE_BIN="$(command -v mise)"
    return
  fi

  log "Installing mise..."
  curl https://mise.run | sh
  if [[ ! -x "$MISE_BIN" ]]; then
    echo "Could not find mise at $MISE_BIN after install." >&2
    exit 1
  fi
}

activate_mise_for_script() {
  # Activate so subsequent commands in this script use the just-installed mise.
  eval "$("$MISE_BIN" activate bash)"
}

install_tools() {
  local failures=0

  for tool in "${TOOLS[@]}"; do
    log "Configuring $tool@latest"
    if ! "$MISE_BIN" use -g "${tool}@latest"; then
      echo "WARN: failed to configure ${tool}@latest" >&2
      failures=$((failures + 1))
    fi
  done

  log "Installing configured tools"
  "$MISE_BIN" install

  log "Installed tool versions"
  "$MISE_BIN" current || true

  if [[ "$failures" -gt 0 ]]; then
    echo "Completed with $failures configuration warning(s)." >&2
    echo "Re-run failed tools manually with: mise use -g <tool>@latest" >&2
    return 1
  fi
}

print_next_steps() {
  cat <<'EOF'

Next steps:
  1) Add mise activation to your shell profile if needed:
       echo 'eval "$(mise activate bash)"' >> ~/.bashrc
  2) Open a new shell or run:
       eval "$(mise activate bash)"
  3) Verify:
       mise current
EOF
}

main() {
  ensure_mise
  activate_mise_for_script
  install_tools
  print_next_steps
}

main "$@"

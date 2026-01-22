#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.claude/commands" "$HOME/.claude/agents"

cp "$ROOT_DIR/.claude/commands/pandas-polars-migration.md" "$HOME/.claude/commands/pandas-polars-migration.md"

if [ -d "$ROOT_DIR/.claude/agents" ]; then
  cp "$ROOT_DIR/.claude/agents/"*.md "$HOME/.claude/agents/" 2>/dev/null || true
fi

echo "Installed:"
echo "- $HOME/.claude/commands/pandas-polars-migration.md"
echo "- $HOME/.claude/agents (router + mode-specific agents, if present)"

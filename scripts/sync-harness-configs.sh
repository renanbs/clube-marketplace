#!/usr/bin/env bash
# ==============================================================================
# sync-harness-configs.sh — Multi-Harness Configuration Pointer Synchronizer
#
# For every AGENTS.md in the target directory, ensures sibling harness files
# exist with the content `@AGENTS.md` so that AGENTS.md remains the single,
# tool-agnostic source of truth across all AI harnesses (Claude Code, Cursor,
# Gemini/Antigravity, OMP).
#
# Usage:
#   ./scripts/sync-harness-configs.sh [TARGET_DIR] [FILENAMES...]
#
# Example:
#   ./scripts/sync-harness-configs.sh . CLAUDE.md GEMINI.md .cursorrules
# ==============================================================================
set -euo pipefail

target_dir="${1:-.}"
shift || true

filenames=("$@")
if [ ${#filenames[@]} -eq 0 ]; then
  filenames=("CLAUDE.md" "GEMINI.md" ".cursorrules")
fi

if [ ! -d "$target_dir" ]; then
  echo "Error: target directory does not exist: $target_dir" >&2
  exit 1
fi

target_dir=$(cd "$target_dir" && pwd)
cd "$target_dir"

created=0
skipped=0
untouched=0

while IFS= read -r -d '' agents_md; do
  dir=$(dirname "$agents_md")

  for filename in "${filenames[@]}"; do
    target="$dir/$filename"

    if [ ! -e "$target" ]; then
      printf '@AGENTS.md\n' > "$target"
      echo "  [CREATED]   $target -> @AGENTS.md"
      created=$((created + 1))
      continue
    fi

    # Read target content safely
    content="$(cat "$target" 2>/dev/null || echo '')"
    if [ "$content" = "@AGENTS.md" ]; then
      untouched=$((untouched + 1))
      continue
    fi

    echo "  [PRESERVED] $target has custom/legacy content (not overwritten)"
    skipped=$((skipped + 1))
  done
done < <(find . -name node_modules -prune -o -name .git -prune -o -name .specs -prune -o -name AGENTS.md -print0)

echo "Harness sync complete: $created created, $untouched aligned, $skipped preserved/custom"

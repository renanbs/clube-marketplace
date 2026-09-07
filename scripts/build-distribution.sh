#!/usr/bin/env bash
# ==============================================================================
# build-distribution.sh — Multi-Harness Artifact Distribution Builder
#
# Copies canonical skills, commands, and shared components into individual
# harness distribution directories (omp, claude-code, cursor, antigravity, opencode).
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Building multi-harness distribution bundles..."

# 1. Sync canonical root skills and commands from base
mkdir -p "$REPO_ROOT/skills" "$REPO_ROOT/commands"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/commands/"

# 2. Oh My Pi (OMP) distribution
mkdir -p "$REPO_ROOT/omp/skills" "$REPO_ROOT/omp/commands" "$REPO_ROOT/omp/.omp-plugin" "$REPO_ROOT/omp/.claude-plugin"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/omp/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/omp/commands/"
cp "$REPO_ROOT/.omp-plugin/plugin.json" "$REPO_ROOT/omp/.omp-plugin/plugin.json"
cp "$REPO_ROOT/.claude-plugin/plugin.json" "$REPO_ROOT/omp/.claude-plugin/plugin.json"

# 3. Claude Code distribution
mkdir -p "$REPO_ROOT/claude-code/skills" "$REPO_ROOT/claude-code/commands" "$REPO_ROOT/claude-code/.claude-plugin"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/claude-code/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/claude-code/commands/"
cp "$REPO_ROOT/.claude-plugin/plugin.json" "$REPO_ROOT/claude-code/.claude-plugin/plugin.json"

# 4. Cursor distribution
mkdir -p "$REPO_ROOT/cursor/skills" "$REPO_ROOT/cursor/commands" "$REPO_ROOT/cursor/.cursor/rules"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/cursor/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/cursor/commands/"
cp "$REPO_ROOT/.cursor/rules/clube-marketplace.mdc" "$REPO_ROOT/cursor/.cursor/rules/clube-marketplace.mdc"

# 5. Google Antigravity distribution
mkdir -p "$REPO_ROOT/antigravity/skills" "$REPO_ROOT/antigravity/commands" "$REPO_ROOT/antigravity/shared" "$REPO_ROOT/antigravity/bin"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/antigravity/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/antigravity/commands/"
cp -r "$REPO_ROOT/base/shared/"* "$REPO_ROOT/antigravity/shared/"
cp "$REPO_ROOT/bin/clube-config" "$REPO_ROOT/antigravity/bin/clube-config"
cp "$REPO_ROOT/.omp-plugin/plugin.json" "$REPO_ROOT/antigravity/plugin.json"

# 6. OpenCode distribution
mkdir -p "$REPO_ROOT/opencode/skills" "$REPO_ROOT/opencode/commands"
cp -r "$REPO_ROOT/base/skills/"* "$REPO_ROOT/opencode/skills/"
cp -r "$REPO_ROOT/base/commands/"* "$REPO_ROOT/opencode/commands/"

echo "Distribution bundles successfully built for OMP, Claude Code, Cursor, Antigravity, and OpenCode."

#!/usr/bin/env bash
# ==============================================================================
# lib-harness.sh — AI Host Harness & Model Role Profile Utilities
#
# Supports detection and profile configuration for:
#   - OMP (Oh My Pi / Orca Agent)
#   - Claude Code
#   - Cursor (IDE / Agent)
#   - Antigravity
#   - OpenCode
#   - Generic Shell
# ==============================================================================
HARNESS_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/clube-marketplace"
HARNESS_PROFILE_FILE="${HARNESS_CONFIG_DIR}/harness-profile.json"

# ANSI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

detect_active_harness() {
    # 1. OMP (Oh My Pi / Orca Agent)
    if [ -n "${OMPCODE:-}" ] || [ -n "${ORCA_OMP_SOURCE_AGENT_DIR:-}" ] || [ -n "${OMP_SESSION_ID:-}" ] || [ -n "${OMP_VERSION:-}" ] || [ -n "${OMP_AGENT:-}" ]; then
        echo "omp"
        return 0
    fi

    # 2. Antigravity native
    if [ -n "${ANTIGRAVITY:-}" ] || [ -n "${ANTIGRAVITY_SESSION:-}" ]; then
        echo "antigravity"
        return 0
    fi

    # 3. Cursor
    if [ -n "${CURSOR_PROJECT_DIR:-}" ] || [ -n "${CURSOR_TRACE:-}" ] || [ -n "${CURSOR_AGENT:-}" ]; then
        echo "cursor"
        return 0
    fi

    # 4. OpenCode
    if [ -n "${OPENCODE:-}" ] || [ -n "${OPENCODE_SESSION:-}" ]; then
        echo "opencode"
        return 0
    fi

    # 5. Claude Code
    if [ -n "${CLAUDE_CONVERSATION_ID:-}" ]; then
        echo "claude-code"
        return 0
    fi

    # 6. Process tree inspection
    local cur_pid=$$
    while [ "$cur_pid" -gt 1 ]; do
        local p_name
        p_name="$(ps -o comm= -p "$cur_pid" 2>/dev/null || echo '')"
        if echo "$p_name" | grep -qiE "^omp"; then
            echo "omp"
            return 0
        elif echo "$p_name" | grep -qiE "^claude"; then
            echo "claude-code"
            return 0
        elif echo "$p_name" | grep -qiE "^cursor"; then
            echo "cursor"
            return 0
        elif echo "$p_name" | grep -qiE "^opencode"; then
            echo "opencode"
            return 0
        fi
        cur_pid="$(ps -o ppid= -p "$cur_pid" 2>/dev/null | tr -d ' ' || echo '1')"
    done

    echo "generic-shell"
}

get_harness_friendly_name() {
    case "$1" in
        omp) echo "Oh My Pi (OMP) + Antigravity" ;;
        claude-code) echo "Claude Code (CLI)" ;;
        cursor) echo "Cursor (IDE / Agent)" ;;
        antigravity) echo "Google Antigravity" ;;
        opencode) echo "OpenCode" ;;
        *) echo "Generic Terminal / Shell" ;;
    esac
}

get_saved_harness() {
    if [ -f "$HARNESS_PROFILE_FILE" ]; then
        grep -oP '(?<="harness": ")[^"]+' "$HARNESS_PROFILE_FILE" 2>/dev/null || echo "none"
    else
        echo "none"
    fi
}

get_saved_model_role() {
    local role="$1"
    if [ -f "$HARNESS_PROFILE_FILE" ]; then
        grep -oP "(?<=\"${role}\": \")[^\"]+" "$HARNESS_PROFILE_FILE" 2>/dev/null || echo "default"
    else
        echo "default"
    fi
}

save_harness_profile() {
    local harness="$1"
    local reasoning="${2:-default}"
    local code="${3:-default}"
    local critique="${4:-default}"
    local security="${5:-default}"

    mkdir -p "$HARNESS_CONFIG_DIR" 2>/dev/null || true
    cat <<EOF > "$HARNESS_PROFILE_FILE"
{
  "harness": "$harness",
  "roles": {
    "reasoning": "$reasoning",
    "code": "$code",
    "critique": "$critique",
    "security": "$security"
  },
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

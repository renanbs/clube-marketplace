#!/usr/bin/env bash
# ==============================================================================
# lib-runlog.sh — Structured Event Logging for AI Marketplace Suite
# ==============================================================================
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/clube-marketplace"
RUNS_DIR="${STATE_DIR}/runs"
CURRENT_RUN_LOG="${RUNS_DIR}/latest.jsonl"

ensure_runlog_dir() {
    mkdir -p "$RUNS_DIR" 2>/dev/null || true
}

runlog_event() {
    local level="${1:-info}"
    local event="${2:-unknown}"
    local details="${3:-}"
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")"

    ensure_runlog_dir
    local json_entry
    json_entry="{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"event\":\"$event\",\"details\":\"$details\"}"

    if [ -d "$RUNS_DIR" ]; then
        echo "$json_entry" >> "$CURRENT_RUN_LOG" 2>/dev/null || true
    fi
}

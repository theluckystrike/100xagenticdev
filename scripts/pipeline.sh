#!/bin/bash
# 100x Agentic Pipeline — Multi-stage autonomous task execution
# Usage: ./pipeline.sh "task description"
set -euo pipefail

TASK="${1:?Usage: ./pipeline.sh 'task description'}"
PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="$PROJECT_DIR/.claude-pipeline/$TIMESTAMP"
BUDGET_MAX=10.00
BUDGET_SPENT=0

mkdir -p "$LOG_DIR"

log() { echo "[$(date +%H:%M:%S)] $1" | tee -a "$LOG_DIR/pipeline.log"; }

track_cost() {
  local result_file="$1"
  local cost
  cost=$(jq -r '.total_cost_usd // 0' "$result_file" 2>/dev/null || echo "0")
  BUDGET_SPENT=$(echo "$BUDGET_SPENT + $cost" | bc)
  local remaining
  remaining=$(echo "$BUDGET_MAX - $BUDGET_SPENT" | bc)
  log "Budget: \$${BUDGET_SPENT}/\$${BUDGET_MAX} (remaining: \$${remaining})"
  if (( $(echo "$BUDGET_SPENT >= $BUDGET_MAX" | bc -l) )); then
    log "BUDGET EXCEEDED. Stopping pipeline."
    exit 1
  fi
}

run_stage() {
  local name="$1"
  local prompt="$2"
  local max_turns="${3:-10}"
  local outfile="$LOG_DIR/$name.json"

  log "=== Stage: $name ==="
  claude -p "$prompt" \
    --dangerously-skip-permissions \
    --output-format json \
    --max-turns "$max_turns" \
    --max-budget-usd "$(echo "$BUDGET_MAX - $BUDGET_SPENT" | bc)" \
    > "$outfile" 2>&1 || true

  track_cost "$outfile"
  jq -r '.result // "No result"' "$outfile" 2>/dev/null
}

# Stage 1: Analyze
run_stage "01-analyze" \
  "Analyze the codebase. Understand the task: '$TASK'. List the files that need to change and why. Output a numbered plan." \
  5

# Stage 2: Implement
PLAN=$(jq -r '.result // ""' "$LOG_DIR/01-analyze.json" 2>/dev/null)
run_stage "02-implement" \
  "Execute this plan:\n$PLAN\n\nAfter each change, verify it compiles and tests pass. Fix any failures." \
  25

# Stage 3: Test
run_stage "03-test" \
  "Run the full test suite. If any tests fail, fix them. Add tests for any uncovered code paths from the changes." \
  15

# Stage 4: Review
run_stage "04-review" \
  "Review all changes made in this session. Check for: security issues, edge cases, code quality. Flag any concerns." \
  5

log "=== Pipeline complete ==="
log "Total cost: \$${BUDGET_SPENT}"
log "Logs: $LOG_DIR/"

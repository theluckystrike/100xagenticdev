#!/bin/bash
# Parallel Agent Executor — Run N Claude instances on isolated git worktrees
# Usage: ./parallel-agents.sh "task1" "task2" "task3"
set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 'task1' 'task2' 'task3' ..."
  exit 1
fi

PROJECT_DIR="$(git rev-parse --show-toplevel)"
WORKTREE_BASE="$PROJECT_DIR/.claude-worktrees"
RESULTS_DIR="$PROJECT_DIR/.claude-pipeline/parallel-$(date +%Y%m%d_%H%M%S)"
MAX_TURNS=30
MAX_BUDGET=2.00

mkdir -p "$WORKTREE_BASE" "$RESULTS_DIR"

PIDS=()
TASKS=("$@")

echo "=== Launching ${#TASKS[@]} parallel agents ==="

for i in "${!TASKS[@]}"; do
  BRANCH="agent-$i-$(date +%s)"
  WORKTREE="$WORKTREE_BASE/agent-$i"

  # Clean stale worktree
  git worktree remove "$WORKTREE" --force 2>/dev/null || true

  # Create isolated worktree
  git worktree add "$WORKTREE" -b "$BRANCH" HEAD

  # Launch agent in background
  (
    cd "$WORKTREE"
    echo "[Agent $i] Starting: ${TASKS[$i]:0:80}..."
    claude -p "${TASKS[$i]}" \
      --dangerously-skip-permissions \
      --output-format json \
      --max-turns "$MAX_TURNS" \
      --max-budget-usd "$MAX_BUDGET" \
      > "$RESULTS_DIR/agent-$i.json" 2>&1

    # Auto-commit if there are changes
    if ! git diff --quiet HEAD 2>/dev/null; then
      git add -A
      git commit -m "Agent $i: ${TASKS[$i]:0:50}..." 2>/dev/null || true
    fi
    echo "[Agent $i] Complete."
  ) &

  PIDS+=($!)
  echo "  Agent $i launched on branch $BRANCH (PID: ${PIDS[-1]})"
done

echo ""
echo "Waiting for all ${#PIDS[@]} agents..."
FAILED=0
for i in "${!PIDS[@]}"; do
  if ! wait "${PIDS[$i]}"; then
    echo "  Agent $i FAILED"
    FAILED=$((FAILED + 1))
  else
    echo "  Agent $i OK"
  fi
done

# Summary
echo ""
echo "=== Results ==="
TOTAL_COST=0
for i in "${!TASKS[@]}"; do
  COST=$(jq -r '.total_cost_usd // 0' "$RESULTS_DIR/agent-$i.json" 2>/dev/null || echo "0")
  TOTAL_COST=$(echo "$TOTAL_COST + $COST" | bc)
  STATUS=$(jq -r '.subtype // "unknown"' "$RESULTS_DIR/agent-$i.json" 2>/dev/null || echo "unknown")
  echo "  Agent $i: $STATUS (\$$COST) — ${TASKS[$i]:0:60}"
done
echo "  Total cost: \$$TOTAL_COST"
echo "  Results: $RESULTS_DIR/"

# Cleanup worktrees
for i in "${!TASKS[@]}"; do
  git worktree remove "$WORKTREE_BASE/agent-$i" --force 2>/dev/null || true
done

echo ""
echo "Review branches: git log --all --oneline --graph"
[ $FAILED -eq 0 ] || exit 1

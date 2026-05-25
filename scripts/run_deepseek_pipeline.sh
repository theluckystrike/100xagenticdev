#!/bin/bash
# DeepSeek 20-Agent Pipeline Runner
# Usage:
#   ./run_deepseek_pipeline.sh --preset crypto_research --topic "DeFi protocols"
#   ./run_deepseek_pipeline.sh --prompt "Research AI agent frameworks" --fan-out 20
#   ./run_deepseek_pipeline.sh --tasks my_tasks.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")/pipeline"

# Verify API key
if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    echo "ERROR: DEEPSEEK_API_KEY not set"
    echo "  export DEEPSEEK_API_KEY=sk-..."
    exit 1
fi

# Verify Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Check httpx
if ! python3 -c "import httpx" 2>/dev/null; then
    echo "Installing httpx..."
    pip3 install httpx
fi

echo "=== 100x DeepSeek Pipeline ==="
echo "  API Key: ${DEEPSEEK_API_KEY:0:8}...${DEEPSEEK_API_KEY: -4}"
echo "  Pipeline: $PIPELINE_DIR"
echo "  Args: $*"
echo ""

cd "$PIPELINE_DIR"
python3 runner.py "$@"

#!/bin/bash
# MCP Server Setup — Install recommended servers for the 100x pipeline
# Run once to configure all MCP servers
set -euo pipefail

echo "=== Setting up MCP Servers ==="

# 1. Knowledge graph memory
echo "[1/7] Memory (knowledge graph)..."
claude mcp add --scope user --transport stdio \
  --env MEMORY_FILE_PATH="$HOME/.claude/memory.jsonl" \
  memory -- npx -y @modelcontextprotocol/server-memory

# 2. Sequential Thinking
echo "[2/7] Sequential Thinking..."
claude mcp add --scope user --transport stdio \
  sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# 3. Filesystem
echo "[3/7] Filesystem..."
claude mcp add --scope user --transport stdio \
  filesystem -- npx -y @modelcontextprotocol/server-filesystem "$HOME/Desktop" "$HOME/Documents" "$HOME/100xagenticdev"

# 4. Context7 (library docs)
echo "[4/7] Context7..."
claude mcp add --scope user --transport stdio \
  context7 -- npx -y @upstash/context7-mcp

# 5. Fetch (web content)
echo "[5/7] Fetch..."
claude mcp add --scope user --transport stdio \
  fetch -- npx -y @modelcontextprotocol/server-fetch

# 6. Playwright (browser automation)
echo "[6/7] Playwright..."
claude mcp add --scope user --transport stdio \
  playwright -- npx -y @playwright/mcp@latest --headless

echo ""
echo "=== Manual Setup Required ==="
echo ""
echo "7. Brave Search (requires API key from https://brave.com/search/api):"
echo "   claude mcp add --scope user --transport stdio \\"
echo "     --env BRAVE_API_KEY=YOUR_KEY \\"
echo "     brave-search -- npx -y @modelcontextprotocol/server-brave-search"
echo ""
echo "8. GitHub (requires PAT from https://github.com/settings/tokens):"
echo "   claude mcp add --scope user --transport http github \\"
echo "     https://api.githubcopilot.com/mcp/ \\"
echo "     --header 'Authorization: Bearer YOUR_GITHUB_PAT'"
echo ""
echo "Verify with: claude mcp list"

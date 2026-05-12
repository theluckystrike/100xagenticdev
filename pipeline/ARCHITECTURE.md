# 100x Agentic Engineer Pipeline — Architecture

**The fully autonomous development pipeline that maximizes developer ROI.**

---

## SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR LAYER                     │
│  Shell scripts / cron / GitHub Actions / Cloud Routines  │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ PLANNING │ CODING   │ REVIEW   │ TESTING  │ DEPLOY      │
│ Agent    │ Agents   │ Agent    │ Agent    │ Agent       │
│ (Opus)   │ (Sonnet) │ (Opus)   │ (Haiku)  │ (Haiku)    │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                    QUALITY GATE LAYER                     │
│  ESLint + tsc + Vitest + Semgrep + Gitleaks + NASA P10  │
├─────────────────────────────────────────────────────────┤
│                    COST CONTROL LAYER                    │
│  Model routing + caching + token budgets + circuit break │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ MCP      │ Memory   │ Evals    │ Observ.  │ Model       │
│ Servers  │ System   │ System   │ Stack    │ Router      │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

---

## LAYER 1: MCP SERVER STACK

### Recommended Setup (copy-paste ready)

```bash
# 1. Knowledge graph memory (persists across sessions)
claude mcp add --scope user --transport stdio \
  --env MEMORY_FILE_PATH=/Users/mike/.claude/memory.jsonl \
  memory -- npx -y @modelcontextprotocol/server-memory

# 2. Brave Search (2K free queries/month)
claude mcp add --scope user --transport stdio \
  --env BRAVE_API_KEY=YOUR_KEY \
  brave-search -- npx -y @modelcontextprotocol/server-brave-search

# 3. GitHub (repos, PRs, issues, actions)
claude mcp add --scope user --transport http github \
  https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

# 4. Context7 (up-to-date library docs)
claude mcp add --scope user --transport stdio context7 \
  -- npx -y @upstash/context7-mcp

# 5. Playwright (headless browser automation)
claude mcp add --scope user --transport stdio playwright \
  -- npx -y @playwright/mcp@latest --headless

# 6. Sequential Thinking (complex reasoning)
claude mcp add --scope user --transport stdio sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking

# 7. Filesystem access (controlled directories)
claude mcp add --scope user --transport stdio filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem /Users/mike/Desktop /Users/mike/Documents

# 8. OpenRouter (route to DeepSeek, GPT, etc.)
# git clone https://github.com/th3nolo/openrouter-mcp.git && cd openrouter-mcp && npm install && npm run build
claude mcp add-json openrouter '{"command":"node","args":["/Users/mike/openrouter-mcp/dist/server.js"],"env":{"OPENROUTER_API_KEY":"YOUR_KEY"}}'

# Verify
claude mcp list
```

### Config File Locations

| Scope | File | Use |
|-------|------|-----|
| Local | `~/.claude.json` (project key) | Only you, only this project |
| Project | `.mcp.json` at project root | Team-shared, git-tracked |
| User | `~/.claude.json` (top-level) | All projects, only you |

---

## LAYER 2: MULTI-AGENT ORCHESTRATION

### Method A: Subagents (Built-In)

Create `.claude/agents/` directory with agent definitions:

**`.claude/agents/security-reviewer.md`:**
```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: sonnet
maxTurns: 20
---
You are a senior security auditor. Analyze for:
- SQL injection, XSS, CSRF
- Insecure auth/session handling
- Hardcoded secrets
- Input validation gaps
Return structured JSON with severity ratings.
```

**`.claude/agents/implementer.md`:**
```markdown
---
name: implementer
description: Implements code changes with tests
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
isolation: worktree
---
When implementing changes:
1. Write the implementation
2. Write tests
3. Run test suite
4. Fix failures
Only report when all tests pass.
```

### Method B: CLI Parallel Execution

```bash
#!/bin/bash
# parallel-agents.sh — Run N Claude instances on isolated worktrees
TASKS=(
  "Refactor src/auth/ to use bcrypt"
  "Add input validation to all API endpoints"
  "Write integration tests for src/payments/"
)

for i in "${!TASKS[@]}"; do
  BRANCH="agent-task-$i-$(date +%s)"
  WORKTREE=".claude-worktrees/agent-$i"
  git worktree add "$WORKTREE" -b "$BRANCH" HEAD

  (
    cd "$WORKTREE"
    claude -p "${TASKS[$i]}" \
      --dangerously-skip-permissions \
      --output-format json \
      --max-turns 30 \
      --max-budget-usd 2.00 \
      > "../agent-$i-result.json" 2>&1
    git add -A && git commit -m "Agent $i: ${TASKS[$i]:0:50}..."
  ) &
done
wait
for i in "${!TASKS[@]}"; do
  git worktree remove ".claude-worktrees/agent-$i" --force 2>/dev/null
done
```

### Method C: Agent Teams (Experimental)

Enable in `~/.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Method D: Agent Farm (20+ Agents)

```bash
pip install claude-code-agent-farm
claude-code-agent-farm --path /your/project --agents 5 \
  --prompt-file prompts/improvement.txt
```

Uses tmux panes, file-lock coordination, auto-restart.

---

## LAYER 3: CLI AUTOMATION PRIMITIVES

### Core Command

```bash
claude -p "prompt" \
  --dangerously-skip-permissions \
  --output-format json \
  --max-turns 15 \
  --max-budget-usd 5.00 \
  --model sonnet
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Non-interactive/headless mode |
| `--output-format json` | Machine-parseable output |
| `--dangerously-skip-permissions` | Full autonomy (no prompts) |
| `--max-turns N` | Cap agentic turns |
| `--max-budget-usd N` | Cost ceiling per call |
| `--model sonnet\|opus\|haiku` | Model selection |
| `--allowedTools "Bash,Read,Write"` | Restrict tools |
| `--worktree` | Isolate in git worktree |
| `--system-prompt "..."` | Override system prompt |

### Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key |
| `ANTHROPIC_BASE_URL` | Proxy/gateway URL |
| `CLAUDE_CODE_MAX_TURNS` | Default turn cap |
| `CLAUDE_CODE_EFFORT_LEVEL` | low/medium/high/max |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable teams |
| `BASH_DEFAULT_TIMEOUT_MS` | Command timeout |

### JSON Output Schema

```json
{
  "type": "result",
  "subtype": "success",
  "result": "response text",
  "session_id": "uuid",
  "total_cost_usd": 0.001234,
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50,
    "cache_read_input_tokens": 1000
  },
  "duration_ms": 2500
}
```

---

## LAYER 4: HOOKS (LIFECYCLE AUTOMATION)

Configure in `.claude/settings.json`:

### Auto-Format on Every Edit
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
      }]
    }]
  }
}
```

### Block Edits to Protected Files
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/protect-files.sh"
      }]
    }]
  }
}
```

### Re-Inject Context After Compaction
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "compact",
      "hooks": [{
        "type": "command",
        "command": "echo 'Reminder: use Bun. Run tests before committing. Current sprint: auth refactor.'"
      }]
    }]
  }
}
```

### Available Hook Events

| Event | When | Can Block? |
|-------|------|-----------|
| PreToolUse | Before tool call | Yes (exit 2) |
| PostToolUse | After tool call | No |
| SessionStart | Session/compaction | No |
| Notification | Claude needs input | No |
| PermissionRequest | Before permission dialog | Yes |

---

## LAYER 5: QUALITY GATES

### NASA Power of 10 ESLint Config

```js
// eslint.config.mjs
export default [{
  rules: {
    "max-lines-per-function": ["error", { max: 60 }],
    "complexity": ["error", 10],
    "max-depth": ["error", 4],
    "no-labels": "error",
    "no-continue": "error",
    "no-var": "error",
    "prefer-const": "error",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-param-reassign": "error",
    "@typescript-eslint/no-floating-promises": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/strict-boolean-expressions": "error",
  }
}];
```

### Full Quality Gate Script

```bash
#!/bin/bash
# scripts/quality-gate.sh
set -euo pipefail
echo "=== 1. Format ===" && npx prettier --check src/
echo "=== 2. Lint ===" && npx eslint --max-warnings 0 src/
echo "=== 3. Types ===" && npx tsc --noEmit
echo "=== 4. Tests ===" && npx vitest run --coverage
echo "=== 5. Security ===" && semgrep --config "p/owasp-top-ten" --error src/
echo "=== 6. Secrets ===" && gitleaks detect --source . --no-git --no-banner
echo "=== 7. Deps ===" && npm audit --audit-level=high
echo "=== ALL GATES PASSED ==="
```

### LLM Code Review Prompt

```json
{
  "scoring": {
    "correctness": { "weight": 0.4, "scale": "1-5" },
    "security": { "weight": 0.3, "scale": "1-5" },
    "simplicity": { "weight": 0.2, "scale": "1-5" },
    "style": { "weight": 0.1, "scale": "1-5" }
  },
  "verdict_rules": {
    "BLOCK": "weighted_total < 2.5 OR security <= 2",
    "REQUEST_CHANGES": "weighted_total < 3.5",
    "APPROVE": "weighted_total >= 3.5"
  }
}
```

---

## LAYER 6: COST CONTROL

### Model Routing Strategy

```
User Request
    │
    ▼
┌────────────────┐
│ Complexity      │
│ Classifier      │
└────────┬───────┘
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│DeepSeek│ │Claude    │
│V4 Flash│ │Opus/Sonnet│
│$0.28/M │ │$3-15/M   │
└────────┘ └──────────┘
```

### Token Budget Enforcement

```yaml
# Budget layers (enforce OUTSIDE agent code)
per_request_max_tool_calls: 12
per_request_max_budget_usd: 2.00
session_max_budget_usd: 20.00
daily_budget_usd: 100.00
consecutive_no_progress_limit: 5
consecutive_failure_limit: 3
```

### DeepSeek V4 Pro Discount (Until May 31, 2026)

| Token Type | Promo/M | List/M | Savings |
|-----------|---------|--------|---------|
| Cache Hit Input | $0.003625 | $0.0145 | 75% |
| Cache Miss Input | $0.435 | $1.74 | 75% |
| Output | $0.87 | $3.48 | 75% |

**V4 Flash:** $0.14/M input, $0.28/M output — **35-100x cheaper** than frontier.

---

## LAYER 7: MEMORY SYSTEM

### Karpathy's LLM Wiki Pattern

```
Conversations → Daily Logs (raw transcripts)
Daily Logs    → Wiki (compiled knowledge)
Wiki          → Next Session (context injection)
```

### Implementation

```
100xagenticdev/
  memory/
    MEMORY.md          ← Always loaded into context
    daily/
      2026-05-12.md    ← Today's raw notes
    wiki/
      patterns.md      ← Compiled patterns
      decisions.md     ← Architectural decisions
      debugging.md     ← Solutions to recurring problems
```

### MCP Memory Server

```bash
claude mcp add --scope user --transport stdio \
  --env MEMORY_FILE_PATH=/Users/mike/100xagenticdev/memory/knowledge-graph.jsonl \
  memory -- npx -y @modelcontextprotocol/server-memory
```

---

## LAYER 8: EVAL SYSTEM

### Shell-Based Eval Runner

```bash
#!/bin/bash
# evals/run-eval.sh
for case_file in evals/cases/*.json; do
  TASK=$(jq -r '.task' "$case_file")
  EXPECTED=$(jq -r '.expected_pattern' "$case_file")
  OUTPUT=$(claude -p "$TASK" --output-format text 2>/dev/null)
  if echo "$OUTPUT" | grep -qP "$EXPECTED"; then
    echo "PASS: $(basename "$case_file")"
  else
    echo "FAIL: $(basename "$case_file")"
  fi
done
```

### Metrics

- **pass@k:** Agent gets it right at least once in k tries (capability)
- **pass^k:** Agent gets it right every time in k tries (reliability)
- If pass@1 < pass@3, agent is capable but inconsistent — add retries

---

## LAYER 9: OBSERVABILITY

### Recommended: Langfuse (Self-Hosted, Free)

```yaml
# docker-compose.yml
services:
  langfuse:
    image: langfuse/langfuse:2
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/langfuse
  db:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=postgres
```

### What to Track

- Cost per feature (tag every request)
- Latency percentiles (p50/p95/p99)
- Cache hit rates
- Error rates by model
- Quality scores (LLM-as-judge)

### Alternatives

| Tool | Setup | Free Tier |
|------|-------|-----------|
| Langfuse | Self-host | Unlimited |
| Helicone | Proxy (2min) | 10K req/mo |
| Braintrust | SDK | 1M spans |

---

## LAYER 10: SCHEDULING

### Claude Code Built-In

```
# Fixed interval
/loop 5m check deployment status

# Cloud routines (survives laptop closure)
/schedule daily PR review at 9am
/schedule in 2 weeks, open cleanup PR removing feature flag
```

### External Cron

```bash
# crontab -e
0 9 * * * cd /project && claude -p "Review yesterday's changes" --dangerously-skip-permissions >> /var/log/review.json 2>&1
0 * * * * cd /project && claude -p "Run npm audit, fix what's fixable" --dangerously-skip-permissions --max-turns 5 2>&1
```

### GitHub Actions

```yaml
on:
  issue_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

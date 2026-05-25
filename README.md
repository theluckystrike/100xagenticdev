# 100x Agentic Engineer Pipeline

> "People who master agentic workflows may outperform others by far more than 10x." — Andrej Karpathy

**One command. 4-stage pipeline. NASA Power of 10 quality gates. Budget enforcement. Dashboard.**

Turn a single developer into a 100-person engineering team through context engineering, multi-agent orchestration, and harness engineering.

## Install (30 seconds)

```bash
git clone https://github.com/theluckystrike/100xagenticdev.git
cd 100xagenticdev
ln -sf "$(pwd)/100x" /usr/local/bin/100x
```

**Requires:** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`)

## Quick Start

```bash
# Initialize your project
cd ~/your-project
100x init

# Run the full 4-stage pipeline
100x run "Add input validation to all API endpoints"

# Run quality gates only
100x gate

# Parallel execution — 3 tasks simultaneously
100x parallel "Add dark mode" "Add i18n" "Add analytics"

# Deep research on any topic
100x research "MCP server ecosystem and monetization"
```

## The Pipeline

Every `100x run` executes 4 stages automatically:

```
┌──────────┐     ┌──────────────┐     ┌────────┐     ┌──────────┐
│ ANALYZE  │ ──→ │  IMPLEMENT   │ ──→ │  TEST  │ ──→ │  REVIEW  │
│          │     │              │     │        │     │          │
│ Read code│     │ Write code   │     │ Run    │     │ Security │
│ Make plan│     │ Follow plan  │     │ tests  │     │ Quality  │
│ Scope    │     │ Verify each  │     │ Fix    │     │ NASA P10 │
│ Risk     │     │ change       │     │ Cover  │     │ OWASP    │
└──────────┘     └──────────────┘     └────────┘     └──────────┘
```

Every stage is wrapped with the **harness** — the context engineering rules that multiply performance 6-10x on the same model.

After completion, an interactive **HTML dashboard** opens automatically showing costs, stage results, and pipeline metrics.

## The 4 ROI Multipliers

| Multiplier | Impact | Evidence |
|-----------|--------|---------|
| **Harness Engineering** | 6-10x on same model | Hashline: 6.7% → 68.3% by changing only the edit format |
| **Model Routing** | 85% cost reduction | RouteLLM: 95% quality with 26% expensive model calls |
| **Prompt Caching** | 90% input savings | ProjectDiscovery: 59% cost cut with caching alone |
| **Loop Budgets** | Prevents $47K incidents | Real: $16-50K in 5hrs, $47K in 11 days without budgets |

## Commands

| Command | What it does |
|---------|-------------|
| `100x run "task"` | Full 4-stage pipeline (analyze → implement → test → review) |
| `100x init` | Initialize project with CLAUDE.md + NASA P10 config |
| `100x gate` | Run 7-stage quality gate (Prettier → ESLint → tsc → Vitest → Semgrep → Gitleaks → npm audit) |
| `100x parallel "t1" "t2"` | Run N tasks in parallel Claude agents |
| `100x research "topic"` | Deep research with harness-boosted agent |
| `100x deepseek --preset X` | Run DeepSeek 20-agent pipeline (needs `DEEPSEEK_API_KEY`) |
| `100x dashboard` | Open latest pipeline dashboard |

## Environment Variables

```bash
BUDGET_MAX=10.00          # Pipeline budget in USD (default: 10)
MAX_TURNS_ANALYZE=8       # Agent turns for analysis stage
MAX_TURNS_IMPLEMENT=30    # Agent turns for implementation
MAX_TURNS_TEST=15         # Agent turns for testing
MAX_TURNS_REVIEW=8        # Agent turns for review
DEEPSEEK_API_KEY=sk-...   # For DeepSeek multi-agent pipeline
```

## Project Setup

Running `100x init` in your project directory:

1. Copies **CLAUDE.md** with NASA P10 rules (if not present)
2. Creates `.100x/runs/` directory for pipeline logs
3. Installs **NASA P10 ESLint config** (for JS/TS projects)
4. Adds `.100x/` to `.gitignore`

## Quality Gates

The `100x gate` command runs 7 checks in fail-fast order (cheapest first):

```
Gate 1: Prettier       — formatting
Gate 2: ESLint         — NASA P10 rules (60-line max, complexity 10, depth 4)
Gate 3: TypeScript     — type safety
Gate 4: Vitest/Jest    — unit tests
Gate 5: Semgrep        — OWASP Top 10 SAST
Gate 6: Gitleaks       — secret detection
Gate 7: npm audit      — dependency CVEs
```

## DeepSeek Multi-Agent Pipeline

For heavy research tasks, use the 20-agent DeepSeek pipeline ($0.14-$0.87/M tokens):

```bash
# Fan-out research across 20 perspectives
100x deepseek --prompt "Analyze the MCP ecosystem" --fan-out 20 --budget 5.0

# Use built-in presets
100x deepseek --preset crypto_research --topic "Solana DeFi"
100x deepseek --preset market_scan --topic "AI developer tools"
100x deepseek --preset sec_audit_recon --topic "OAuth 2.0 libraries"
100x deepseek --preset code_review --topic "the authentication module"

# Available presets: crypto_research, market_scan, competitive_intel,
#                    sec_audit_recon, code_review, seo_research,
#                    domain_research, tech_deep_dive
```

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR LAYER                        │
│   100x CLI · Shell scripts · Cron · GitHub Actions            │
├─────────┬─────────┬─────────┬─────────┬─────────┬───────────┤
│  PLAN   │  CODE   │ REVIEW  │  TEST   │ DEPLOY  │ MCP       │
│  Agent  │ Agents  │ Agent   │ Agent   │ Agent   │ SERVERS   │
├─────────┴─────────┴─────────┴─────────┴─────────┴───────────┤
│                    HARNESS LAYER (6-10x)                      │
│  CLAUDE.md · Context injection · Stage prompts · NASA P10     │
├──────────────────────────────────────────────────────────────┤
│                    QUALITY GATE LAYER                         │
│  Prettier → ESLint → tsc → Vitest → Semgrep → Gitleaks      │
├──────────────────────────────────────────────────────────────┤
│                    COST CONTROL LAYER                         │
│  Model routing · Prompt caching · Token budgets · Evals       │
└──────────────────────────────────────────────────────────────┘
```

## What's Included

```
100xagenticdev/
├── 100x                              # CLI entry point (symlink this)
├── CLAUDE.md                         # Project rules template
├── config/
│   ├── nasa-p10-eslint.config.mjs    # ESLint rules for NASA P10
│   ├── hooks-settings.json           # Claude Code hooks
│   └── mcp-setup.sh                  # MCP server installer
├── scripts/
│   ├── pipeline.sh                   # Standalone 4-stage pipeline
│   ├── parallel-agents.sh            # Git worktree parallel agents
│   └── quality-gate.sh               # Quality gate runner
├── pipeline/
│   ├── orchestrator.py               # 20-agent async orchestrator
│   ├── deepseek_client.py            # DeepSeek API client
│   ├── runner.py                     # CLI runner for DeepSeek pipeline
│   ├── task_templates.py             # 8 preset task sets
│   └── aggregator.py                 # Dashboard HTML generator
└── research/
    ├── 1000x-agentic-developer-report.md
    ├── karpathy-definitive-study.md
    └── ...
```

## The Formula

```
100x = CLAUDE.md rules
     + Harness engineering    (6-10x on same model)
     + Model routing          (75-85% cost reduction)
     + Prompt caching         (90% input savings)
     + Eval loops             (quality maintenance)
     + Loop budgets           (prevents $47K incidents)
     + Multi-agent            (parallel execution)
     + Memory system          (compounding knowledge)
```

## Based On

- [Karpathy's Context Engineering](https://x.com/karpathy/status/1937902205765607626) — "The hottest new programming language is English"
- [RouteLLM (ICLR 2025)](https://www.lmsys.org/blog/2024-07-01-routellm/) — 85% cost reduction with quality routing
- [Anthropic: Demystifying Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Production agent evaluation
- [NASA JPL Power of 10](https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code) — Zero-defect coding rules

## License

MIT

---

*"You can outsource your thinking, but you can't outsource your understanding."*

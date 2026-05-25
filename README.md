# 100x Agentic Engineer Pipeline

> "People who master agentic workflows may outperform others by far more than 10x." — Andrej Karpathy

**One command. 4-stage pipeline. NASA Power of 10 quality gates. Budget enforcement. Dashboard.**

Turn a single developer into a 100-person engineering team through context engineering, multi-agent orchestration, and harness engineering.

## Install (30 seconds)

```bash
git clone https://github.com/theluckystrike/100xagenticdev.git
cd 100xagenticdev
ln -sf "$(pwd)/100x" /usr/local/bin/100x

# Check prerequisites
100x doctor
```

**Requires:** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`), `jq`, `git`, `bc`

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
| `100x gate` | Auto-detect project type and run quality gates |
| `100x parallel "t1" "t2"` | Run N tasks in parallel with git worktree isolation |
| `100x research "topic"` | Deep research with harness-boosted agent |
| `100x history` | Show past pipeline runs with costs |
| `100x doctor` | Check all prerequisites |
| `100x config set k v` | Persistent settings (~/.100x.json) |
| `100x deepseek --preset X` | Run DeepSeek 20-agent pipeline (needs `DEEPSEEK_API_KEY`) |
| `100x dashboard` | Open latest pipeline dashboard |

## Configuration

Persistent settings via `100x config`:

```bash
100x config set budget_max 25        # USD budget per run
100x config set autonomous true      # Non-interactive mode
100x config set src_dir lib          # Custom source directory
```

Or environment variables (override config):

```bash
BUDGET_MAX=25 100x run "task"
AUTONOMOUS=true 100x run "task"
DEEPSEEK_API_KEY=sk-... 100x deepseek --preset crypto_research
```

## Project Setup

Running `100x init` in your project directory:

1. Copies **CLAUDE.md** with NASA P10 rules (if not present)
2. Creates `.100x/runs/` directory for pipeline logs
3. Installs **NASA P10 ESLint config** (for JS/TS projects)
4. Adds `.100x/` to `.gitignore`

## Quality Gates

`100x gate` auto-detects your project type and runs the appropriate checks:

| Project | Gates |
|---------|-------|
| **JS/TS** (package.json) | Prettier → ESLint → tsc → Vitest → Semgrep → Gitleaks → npm audit |
| **Rust** (Cargo.toml) | cargo fmt → clippy → test → audit → Gitleaks |
| **Go** (go.mod) | gofmt → go vet → test → govulncheck → Gitleaks |
| **Python** (pyproject.toml) | ruff → mypy → pytest → Semgrep → Gitleaks |

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

MIT — see [LICENSE](LICENSE)

---

*"You can outsource your thinking, but you can't outsource your understanding."*

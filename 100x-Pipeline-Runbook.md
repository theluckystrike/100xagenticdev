# 100x Agentic Pipeline — Runbook

> One command. 100 parallel agents. $0.60 per run. Share with your PM.

## Quick Start (30 seconds)

```bash
# 1. Clone & install
git clone https://github.com/theluckystrike/100xagenticdev.git
cd 100xagenticdev
ln -sf "$(pwd)/100x" /usr/local/bin/100x
100x doctor

# 2. Set your DeepSeek API key (get one at platform.deepseek.com)
export DEEPSEEK_API_KEY="sk-your-key-here"

# 3. Run 100 agents on any topic
cd pipeline
python3 runner.py \
  --tasks bln_100_agents.json \
  --agents 20 \
  --budget 10.0 \
  --output ./results/my_run

# 4. Generate dashboard & open
python3 aggregator.py ./results/my_run/ ./results/my_run/dashboard.html
open ./results/my_run/dashboard.html
```

---

## How to Create Your Own 100-Agent Run

### Step 1: Copy the Template

```bash
cp pipeline/bln_100_agents.json pipeline/my_project.json
```

### Step 2: Edit the Task File

The file has this structure:

```json
{
  "phases": [
    {
      "tasks": [
        {
          "task_id": "phase1-01",
          "prompt": "CONTEXT: [Your product/company details]\n\nTASK: [Specific research question]",
          "system_prompt": "You are a [expert role]. Focus on [angle].",
          "temperature": 0.5,
          "max_tokens": 4096
        }
      ],
      "synthesis_prompt": "Synthesize all findings into..."
    }
  ]
}
```

**Design rules:**
- 5 phases x 20 tasks = 100 agents
- Each phase runs 20 agents IN PARALLEL (fast)
- Phase N output feeds into Phase N+1 (compounding intelligence)
- Each phase has a synthesis agent that consolidates all 20 results
- Put your full product context in EVERY prompt (agents don't share memory)

### Step 3: Design Your 5 Phases

| Phase | Purpose | Agent Types |
|-------|---------|------------|
| **1. Research** | Gather raw data | Market size, competitors, pricing, trends |
| **2. Strategy** | Design approaches | Growth, distribution, conversion, retention |
| **3. Product** | Build the plan | Features, architecture, UX, roadmap |
| **4. Execution** | Plan the work | Timeline, team, budget, risks, operations |
| **5. Validation** | Challenge everything | Devil's advocate, risk analysis, reality checks |

### Step 4: Run It

```bash
cd 100xagenticdev/pipeline

python3 runner.py \
  --tasks my_project.json \
  --agents 20 \
  --budget 10.0 \
  --output ./results/my_project_run
```

### Step 5: Generate Dashboard

```bash
python3 aggregator.py ./results/my_project_run/ ./results/my_project_run/dashboard.html
open ./results/my_project_run/dashboard.html
```

---

## Built-In Presets (No Custom File Needed)

```bash
# Market research
100x deepseek --preset market_scan --topic "your market"

# Competitive intelligence
100x deepseek --preset competitive_intel --topic "your industry"

# Security audit
100x deepseek --preset sec_audit_recon --topic "your target"

# Code review
100x deepseek --preset code_review --topic "your codebase area"

# SEO research
100x deepseek --preset seo_research --topic "your keywords"

# Technology deep dive
100x deepseek --preset tech_deep_dive --topic "your tech stack"

# Domain research
100x deepseek --preset domain_research --topic "your domain"

# Crypto research
100x deepseek --preset crypto_research --topic "your protocol"
```

Each preset runs 20 agents with expert-designed prompts.

---

## Fan-Out Mode (Quick Custom Research)

Don't want to create a JSON file? Fan out a single prompt across 20 perspectives:

```bash
100x deepseek \
  --prompt "Analyze the competitive landscape for AI writing tools and find the 10 biggest opportunities" \
  --fan-out 20 \
  --budget 5.0
```

This automatically creates 20 variants covering: quantitative, qualitative, risks, opportunities, competitive, technical, historical, regulatory, UX, financial, contrarian, supply chain, team, timeline, adjacent markets, moats, distribution, tech stack, ecosystem, macro trends.

---

## For Code Changes (Claude Code Pipeline)

```bash
# Initialize your project (one time)
cd ~/your-project
100x init

# Run full 4-stage pipeline: Analyze → Implement → Test → Review
100x run "Add input validation to all API endpoints"

# Run 3 tasks in parallel with git worktree isolation
100x parallel "Add dark mode" "Add i18n" "Add analytics"

# Quality gates only
100x gate

# Deep research
100x research "How to implement WebSocket auth"
```

---

## Cost Reference

| Command | Agents | Typical Cost | Runtime |
|---------|--------|-------------|---------|
| `100x deepseek --preset X` | 20 | $0.03 - $0.08 | 1-2 min |
| `--fan-out 20` | 20 | $0.04 - $0.10 | 1-2 min |
| Custom 100 agents | 100 | $0.30 - $1.00 | 8-12 min |
| `100x run` (Claude) | 1 | $0.50 - $5.00 | 5-15 min |
| `100x parallel` (3 tasks) | 3 | $1.50 - $15.00 | 5-15 min |
| `100x gate` | 0 | Free | 1-3 min |

**DeepSeek pricing (V4 promo until May 31, 2026):**
- Input: $0.435/M tokens (cache hit: $0.003625/M)
- Output: $0.87/M tokens

---

## Example: Run for a New Project

Say you're building a SaaS todo app and want strategic analysis:

```bash
# 1. Copy and edit the template
cp pipeline/bln_100_agents.json pipeline/todo_saas.json

# 2. Find-replace in the file:
#    - "BeLikeNative" → "TodoApp"
#    - Update all CONTEXT sections with YOUR product details
#    - Update metrics (users, revenue, pricing, features)
#    - Adjust research questions to YOUR market

# 3. Run
cd pipeline
DEEPSEEK_API_KEY="sk-xxx" python3 runner.py \
  --tasks todo_saas.json \
  --agents 20 \
  --budget 10.0 \
  --output ./results/todo_saas

# 4. Dashboard
python3 aggregator.py ./results/todo_saas/ ./results/todo_saas/dashboard.html
open ./results/todo_saas/dashboard.html
```

---

## Prompt Engineering Tips for Best Results

1. **Always include full context** in every prompt — agents don't share memory
2. **Be specific** — "Analyze the top 15 competitors with pricing, users, revenue" > "Do competitive analysis"
3. **Give each agent a role** via system_prompt — "You are a pricing strategist" focuses output
4. **Use lower temperature (0.4-0.5)** for data/analysis, higher (0.7-0.9) for creative/strategy
5. **Put the most important question last** — agents pay more attention to the end of prompts
6. **Phase 5 should always be validation** — devil's advocate agents catch optimism bias
7. **The synthesis prompt is critical** — tell it exactly what output format you want

---

## Requirements

- Python 3.9+
- `pip install httpx` (only dependency)
- DeepSeek API key ($5 credit on signup)
- For Claude pipeline: Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)
- `jq`, `git`, `bc` (for the bash CLI)

---

## Repo

```
https://github.com/theluckystrike/100xagenticdev
```

MIT License. Star it if useful.

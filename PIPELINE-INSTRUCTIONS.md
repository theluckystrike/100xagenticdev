# 100x Agentic Pipeline — Run 100 AI Agents in Parallel for $0.60

## Setup (30 seconds)

```bash
git clone https://github.com/theluckystrike/100xagenticdev.git
cd 100xagenticdev
pip install httpx
```

Get a DeepSeek API key: https://platform.deepseek.com ($5 free credit on signup)

---

## Option 1: Run a Preset (fastest — no config needed)

```bash
cd pipeline
DEEPSEEK_API_KEY="sk-your-key" python3 runner.py --preset market_scan --topic "your topic here" --agents 20 --budget 5.0
```

### Available Presets

| Preset | What it does | Default Agents |
|--------|-------------|----------------|
| `market_scan` | Market sizing, trends, opportunities | 20 |
| `competitive_intel` | Competitor analysis | 10 |
| `code_review` | Codebase quality review | 5 |
| `sec_audit_recon` | Security audit recon | 10 |
| `seo_research` | Keyword & SEO strategy | 10 |
| `tech_deep_dive` | Technology analysis | 10 |
| `domain_research` | Domain/industry research | 5 |
| `crypto_research` | DeFi/token deep research | 20 |

### Preset Examples

```bash
DEEPSEEK_API_KEY="sk-..." python3 runner.py --preset competitive_intel --topic "Cursor IDE" --agents 10
DEEPSEEK_API_KEY="sk-..." python3 runner.py --preset sec_audit_recon --topic "Solidity reentrancy" --agents 10
DEEPSEEK_API_KEY="sk-..." python3 runner.py --preset seo_research --topic "claudhq.com" --agents 10
DEEPSEEK_API_KEY="sk-..." python3 runner.py --preset crypto_research --topic "DeFi protocols" --agents 20 --budget 10.0
```

---

## Option 2: Fan-Out Mode (one prompt → 20 parallel perspectives)

```bash
cd pipeline
DEEPSEEK_API_KEY="sk-your-key" python3 runner.py --prompt "Research topic here" --fan-out 20 --budget 5.0
```

Each agent gets the same prompt but a different perspective lens (quantitative, risks, opportunities, competitive, technical, contrarian, regulatory, etc.) — 20 built-in perspectives.

---

## Option 3: Custom 100-Agent Run (JSON file)

```bash
cd pipeline
DEEPSEEK_API_KEY="sk-your-key" python3 runner.py --tasks my_project.json --agents 20 --budget 10.0 --output ./results/my_run
```

To customize: copy `pipeline/bln_100_agents.json`, replace the company context and questions with yours. Structure is 5 phases × 20 agents = 100 parallel researchers.

---

## Generate the HTML Dashboard

After any run completes:

```bash
python3 aggregator.py ./results/run_TIMESTAMP/ ./results/run_TIMESTAMP/dashboard.html
open ./results/run_TIMESTAMP/dashboard.html
```

---

## Dry Run (preview without executing)

```bash
python3 runner.py --preset crypto_research --topic "DeFi" --dry-run
```

---

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--tasks FILE` | — | Path to tasks JSON file |
| `--preset NAME` | — | Use a built-in preset |
| `--prompt TEXT` | — | Single prompt to fan out |
| `--topic TEXT` | — | Topic override for presets |
| `--fan-out N` | 20 | Parallel variants for `--prompt` mode |
| `--agents N` | 20 | Max concurrent agents |
| `--model NAME` | deepseek-chat | DeepSeek model |
| `--budget N` | 10.0 | Budget limit in USD |
| `--output DIR` | auto | Output directory |
| `--temperature N` | 0.7 | Sampling temperature |
| `--max-tokens N` | 4096 | Max tokens per response |
| `--json-mode` | off | Request JSON output |
| `--dry-run` | off | Preview without executing |

---

## Cost

| Run Type | Agents | Estimated Cost |
|----------|--------|---------------|
| Single preset (4K tokens/agent) | 20 | ~$0.03-0.08 |
| Deep research (8K tokens/agent) | 20 | ~$0.15 |
| Crypto preset (2 phases) | 23 | ~$0.15 |
| Full 100-agent custom run | 100 | ~$0.30-1.00 |

Runtime: 2-10 minutes depending on agent count and response length.

Pricing: DeepSeek V4 Flash at $0.14/M input, $0.28/M output.

---

## Architecture

```
runner.py           → CLI entry point (args, modes, budget)
orchestrator.py     → 20-agent parallel execution engine (async)
deepseek_client.py  → Async API client (httpx, retries, circuit breaker)
task_templates.py   → 8 preset research templates
aggregator.py       → Results → HTML dashboard
```

---

## Repo

https://github.com/theluckystrike/100xagenticdev

# 100x DeepSeek Pipeline — Quick Start

## Prerequisites
```bash
export DEEPSEEK_API_KEY=sk-...  # already in env
pip3 install httpx              # already installed
```

## Usage

### 1. Fan-Out Mode (fastest start)
Single prompt → 20 parallel agents with different perspectives → synthesized report:
```bash
cd pipeline/
python3 runner.py --prompt "Research topic here" --fan-out 20 --budget 5.0
```

### 2. Preset Mode (pre-built research templates)
```bash
python3 runner.py --preset crypto_research --topic "DeFi protocols" --agents 20 --budget 10.0
python3 runner.py --preset market_scan --topic "AI developer tools" --agents 20
python3 runner.py --preset competitive_intel --topic "Cursor IDE" --agents 10
python3 runner.py --preset sec_audit_recon --topic "Solidity reentrancy" --agents 10
python3 runner.py --preset seo_research --topic "claudhq.com" --agents 10
python3 runner.py --preset tech_deep_dive --topic "DeepSeek V4 architecture" --agents 10
```

### 3. Custom Tasks (JSON file)
```bash
python3 runner.py --tasks example_tasks.json --agents 20 --budget 10.0
```

### 4. Dry Run (preview without executing)
```bash
python3 runner.py --preset crypto_research --dry-run
```

### 5. Generate Dashboard (after run)
```bash
python3 aggregator.py ./results/run_TIMESTAMP/ dashboard.html
```

## Available Presets
| Preset | Description | Default Agents |
|--------|-------------|----------------|
| `crypto_research` | Multi-phase DeFi/token research | 20 |
| `market_scan` | Broad market opportunity scanning | 20 |
| `competitive_intel` | Competitive intelligence | 10 |
| `sec_audit_recon` | Security audit reconnaissance | 10 |
| `code_review` | Distributed code review | 5 |
| `seo_research` | SEO and content strategy | 10 |
| `domain_research` | Domain valuation | 5 |
| `tech_deep_dive` | Technical analysis | 10 |

## Cost Estimates (DeepSeek V4 promo pricing)
| Task | Agents | Est. Cost |
|------|--------|-----------|
| 20-agent fan-out (4K tokens each) | 20 | ~$0.07 |
| Crypto research preset (2 phases) | 20+3 | ~$0.15 |
| Full market scan | 20 | ~$0.07 |
| 20-agent deep research (8K tokens) | 20 | ~$0.15 |

## Architecture
```
runner.py           → CLI entry point
orchestrator.py     → 20-agent parallel execution engine
deepseek_client.py  → Async API client (httpx, retries, circuit breaker)
task_templates.py   → Pre-built research task presets
aggregator.py       → Results collection + HTML dashboard
```

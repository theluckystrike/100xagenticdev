# Autonomous SC Audit Pipeline — A-to-Z Blueprint

**Date:** 2026-05-12
**Sources:** 6 parallel research agents, 200+ web sources, platform documentation, on-chain data
**Objective:** Fully autonomous pipeline from contest discovery to payment collection

---

## EXECUTIVE SUMMARY

### The Answer to "Who Pays and Why?"

**Who pays:** Every DeFi protocol that wants to launch, get listed on exchanges, get insurance coverage, or comply with MiCA regulation (legally required in EU as of July 1, 2026). 500K+ contracts deployed per month. $3.4B stolen in 2025.

**Why they pay:** Because the alternative is getting hacked for $100M+. A $50K audit is insurance. A $10M Immunefi bounty that prevents a $320M exploit is 32:1 ROI.

**How you get paid:** USDC to your Ethereum wallet. Platforms handle distribution. Zero invoicing. Zero sales calls. Zero client acquisition.

**The distribution insight:** The platforms ARE the distribution. Zero CAC. You walk in and compete. 20-30+ contests per month across Code4rena, Sherlock, CodeHawks, Cantina, Hats Finance. 650+ active Immunefi bounty programs with $162M+ available rewards.

### The Gap Nobody Has Filled

All the individual tools exist — MCP servers, Claude Code audit skills, PoC generators, static analysis. **NOBODY has connected: contest monitoring → auto-analysis → auto-submission.** The orchestration layer is the opportunity, and it's exactly what agentic engineering skills are built for.

---

## THE MONEY FLOW: A-TO-Z

### Step 1: Protocol Needs Audit
Protocol raises $10M → allocates 1-5% ($100K-$500K) to security → submits to Code4rena/Sherlock/Cantina → deposits USDC into prize pool

### Step 2: Contest Opens (YOU DO NOTHING — IT COMES TO YOU)
Platform publishes contest → code appears on GitHub → prize pool is locked

### Step 3: Your Pipeline Runs Autonomously
Contest detected → repo cloned → static analysis → DeepSeek 5-agent scan → Claude synthesis → PoC generated → report formatted

### Step 4: Submission
Findings submitted to platform (web form or GitHub PR)

### Step 5: Judging
Platform judges validate findings (2-6 weeks)

### Step 6: Payment
USDC sent directly to your Ethereum wallet. No invoice. No negotiation. Algorithmic distribution based on finding severity and uniqueness.

---

## PLATFORM PAYMENT MECHANICS

| Platform | Token | Chain | Submission | KYC | Payout Timeline | Monitoring |
|----------|-------|-------|-----------|-----|-----------------|------------|
| **Code4rena** | USDC | Ethereum | Web form | Tax info required | 2-6 weeks post-judging | Scrapers, Daily Warden |
| **Sherlock** | USDC | Ethereum | Private GitHub repo | Payout criteria gate | 3-6 weeks | GitHub org monitor |
| **CodeHawks** | USDC | ZKsync | Web portal | Per-competition | After judging | Solodit aggregator |
| **Hats Finance** | USDC | Arbitrum | On-chain tx ($0.30) | None | 17-24 days | On-chain events |
| **Immunefi** | USDC/ETH/native | Ethereum | Web dashboard | zkPassport + per-program | 2-8 weeks | **REST API exists** |
| **Cantina** | USDC | Ethereum | Cantina Code | Mandatory (Persona) | Within 30 days | Web scraping |

### Key Payout Rules
- **Sherlock:** Must have 2+ valid issues AND 20%+ valid ratio before ANY payout
- **Hats Finance:** First-unique-only — duplicates get nothing
- **Code4rena:** 96% conditional pool — refunded if no High/Medium found (zero platform fee for protocols)
- **CodeHawks First Flights:** Weekly, but NO monetary prizes (XP only) — use for practice

### Sherlock Lead Senior Watson Pay (Fixed, Guaranteed)
- Top 33% ranked: **$12,500/week**
- Top 67% ranked: **$10,000/week**
- Top 100% ranked: **$7,500/week**

### Cantina/Spearbit Fellowship Rates
- JSR: $3,000/week → ASR: $6,250/week → SR: $12,500/week → **LSR: $20,000/week**

---

## THE FULLY AUTONOMOUS PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│              AUTONOMOUS SC AUDIT PIPELINE v1.0              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LAYER 1: CONTEST DISCOVERY (24/7 daemon)           │   │
│  │                                                     │   │
│  │  Daily Warden emails ──┐                            │   │
│  │  Solodit aggregator ───┤                            │   │
│  │  GitHub org watchers ──┤──→ Contest Queue (Redis)    │   │
│  │  Immunefi REST API ────┤    Priority: pool/nSLOC    │   │
│  │  Hats on-chain events ─┤    Auto-clone repos        │   │
│  │  Twitter/Discord bots ─┘    Extract scope files     │   │
│  └──────────────────────────────┬──────────────────────┘   │
│                                 │                           │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  LAYER 2: STATIC ANALYSIS (local, $0)               │   │
│  │                                                     │   │
│  │  Slither (90+ detectors) ──┐                        │   │
│  │  Aderyn (Cyfrin, Rust) ────┤──→ JSON findings       │   │
│  │  Mythril (symbolic exec) ──┤    AST parse           │   │
│  │  Solidity Metrics ─────────┘    Call graph           │   │
│  └──────────────────────────────┬──────────────────────┘   │
│                                 │                           │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  LAYER 3: DeepSeek MULTI-AGENT ANALYSIS ($0.18)     │   │
│  │                                                     │   │
│  │  Agent 1: Function-by-function ────┐                │   │
│  │  Agent 2: Cross-contract ──────────┤                │   │
│  │  Agent 3: Pattern matching ────────┤──→ Raw findings│   │
│  │  Agent 4: Economic/game theory ────┤    (70-85% FP) │   │
│  │  Agent 5: Access control ──────────┘                │   │
│  │                                                     │   │
│  │  Via LiteLLM Router:                                │   │
│  │  V4 Flash $0.014/M (cached) → R1 $0.055/M → Claude │   │
│  └──────────────────────────────┬──────────────────────┘   │
│                                 │                           │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  LAYER 4: SYNTHESIS + POC (Claude Sonnet, $0.48)    │   │
│  │                                                     │   │
│  │  Deduplicate across agents                          │   │
│  │  Filter false positives (85% → 30%)                 │   │
│  │  Generate Foundry PoC tests                         │   │
│  │  Run `forge test` to validate PoCs                  │   │
│  │  Severity classification                            │   │
│  │  Format platform-specific reports                   │   │
│  └──────────────────────────────┬──────────────────────┘   │
│                                 │                           │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  LAYER 5: SUBMISSION                                │   │
│  │                                                     │   │
│  │  Code4rena: Playwright → web form                   │   │
│  │  Sherlock:  GitHub API → private repo issues        │   │
│  │  Hats:     ethers.js → Arbitrum on-chain tx         │   │
│  │  Immunefi: Playwright → web dashboard               │   │
│  │  Cantina:  Playwright → Cantina Code                │   │
│  │                                                     │   │
│  │  Human-in-loop option: queue for 60-sec review      │   │
│  └──────────────────────────────┬──────────────────────┘   │
│                                 │                           │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  LAYER 6: PAYMENT + FEEDBACK LOOP                   │   │
│  │                                                     │   │
│  │  Wallet monitor (ethers.js) → detect USDC inflows   │   │
│  │  Track earnings per platform per contest             │   │
│  │  Scrape judging results post-contest                │   │
│  │  Compare submitted vs accepted findings             │   │
│  │  Auto-tune agent prompts (what was missed?)         │   │
│  │  Update vulnerability pattern database              │   │
│  │  Revenue dashboard (real-time)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LAYER 7: CONTENT FLYWHEEL (parallel daemon)        │   │
│  │                                                     │   │
│  │  Forta Network → exploit alerts (real-time)         │   │
│  │  DefiLlama Hacks API → new exploits                 │   │
│  │  AI agent → root cause analysis                     │   │
│  │  Auto-draft Twitter threads                         │   │
│  │  X API → auto-post ($0.015/tweet)                   │   │
│  │  Cost: $30-50/month                                 │   │
│  │  Result: reputation → private audit inbound         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Autonomy Assessment Per Layer

| Layer | 100% Autonomous? | Human Needed? |
|-------|-----------------|---------------|
| 1. Discovery | YES | No |
| 2. Static Analysis | YES | No |
| 3. DeepSeek Analysis | YES | No |
| 4. Synthesis + PoC | 90% | Review flagged edge cases |
| 5. Submission | 80% | 60-sec review before submit (optional) |
| 6. Payment | YES | No |
| 7. Content Flywheel | 90% | Occasional engagement replies |

**Total human time per contest: 30-60 minutes** (review findings, approve submissions). The pipeline handles 95% autonomously.

---

## WHAT EXISTS vs. WHAT YOU BUILD

### Already Built (Use These)

| Tool | What | Source |
|------|------|--------|
| **Slither MCP** | Static analysis via MCP for LLMs | Trail of Bits |
| **Aderyn MCP** | Fast Rust-based analysis via MCP | Cyfrin |
| **Trail of Bits Claude Code Skills** | Audit workflows, vuln detection | github.com/trailofbits/skills |
| **Forefy .context Skills** | Multi-expert audit framework | github.com/forefy/.context |
| **QuillAudits Skills** | 10 specialized audit skills | QuillShield |
| **Immunefi MCP Server** | Query bounty program data | mcpmarket.com |
| **Immunefi ibb CLI** | Search/filter bounty programs | infosec-us-team |
| **Immunefi DAF** | Daily code change feed | infosec-us-team |
| **Daily Warden** | Email digest of all contests | dailywarden.com |
| **Solodit** | Cross-platform finding aggregator | Cyfrin |
| **SmartGuard** | Multi-agent audit with PoC gen | Open source |
| **Aether** | 6-pass LLM pipeline | Open source |
| **LiteLLM** | LLM router/proxy | Open source |

### The Gap You Fill (Your Orchestration Layer)

| Component | What to Build |
|-----------|--------------|
| **Contest Monitor Daemon** | Scrape/poll all platforms, auto-detect new contests, queue them |
| **Auto-Cloner** | Clone contest repos, extract in-scope files, prepare for analysis |
| **Pipeline Orchestrator** | Connect static → DeepSeek → Claude → PoC → submission |
| **Submission Automator** | Playwright scripts for each platform's web form |
| **Feedback Learner** | Scrape judging results, compare predictions, tune prompts |
| **Revenue Dashboard** | Track earnings across all platforms, compute ROI |

---

## THE DEMAND — WHY THE MONEY WON'T STOP

### Structural Forces Creating Mandatory Demand

1. **$3.4B stolen in 2025.** Getting worse, not better. Q1 2025 was worst quarter ever ($1.64B).
2. **MiCA (July 1, 2026).** EU regulation makes smart contract security assessments LEGALLY REQUIRED for any entity serving EU clients.
3. **Exchange listings require audits.** Binance, Coinbase, all Tier-1 exchanges — mandatory pre-listing audit from recognized firm.
4. **Insurance requires audits.** Nexus Mutual, InsurAce — unaudited protocols can't get coverage.
5. **8.7M contracts deployed Q4 2025** on Ethereum alone (record). 500K+/month.
6. **Supply deficit.** Top firms have 2-3 month backlogs. Rush premiums of 20-50%.
7. **94% of long-running Immunefi programs surfaced at least one critical.** Bug bounties are proven insurance.

### Contest Volume (Current)

| Platform | Historical Contests | Typical Pool | Active Frequency |
|----------|-------------------|-------------|-----------------|
| Code4rena | 475+ | $22K-$500K | 4-6/week |
| Sherlock | 297+ | $41K-$2M | 2-4/week |
| CodeHawks | Growing | Varies | Weekly First Flights |
| Cantina | Growing | Varies | 1-3/week |
| Hats Finance | Ongoing | Token-based | 1-2/week |
| **Combined** | | | **8-16/week** |

**At any given time: 3-8 contests running simultaneously.** Your pipeline enters ALL of them.

### Immunefi: The Always-On Lottery

- 650+ active programs
- $162M+ available rewards
- Largest bounties: Usual ($16M), Uniswap v4 ($15.5M), LayerZero ($15M), Wormhole ($10M)
- **REST API exists** for programmatic monitoring
- **DAF tool** tracks daily code changes in bounty-listed repos
- A single critical finding = $10K-$10M payout

---

## VALIDATION: AI AUDIT ACTUALLY WORKS

### Anthropic's Own Research (2026)
- Claude and GPT-5 tested against smart contracts
- **$4.6M in exploits found** across contracts exploited after model knowledge cutoffs
- On SCONE-bench (405 contracts): **51.11% exploit rate, $550.1M in simulated stolen funds**
- Found **2 novel zero-day vulnerabilities** in 2,849 recently deployed contracts

### Nethermind AuditAgent (Production)
- **42% of Critical findings** also identified by tool
- **43% of High findings** also identified
- **62% of audited projects** had valid issues detected
- GitHub Action + REST API for CI/CD

### LLM-SmartAudit (Research, 2025)
- Multi-agent approach: Project Manager + Auditor + Solidity Expert
- **74% recall** (vs Slither's 46%) on Code4rena data
- 6,454 contracts across 102 projects

### Code4rena Bot Races (Operational)
- LightChaser: 800+ detectors, top placement across 60+ races
- Bot findings explicitly separated from human awards
- Pipeline needs to find Medium/High that bots MISS

---

## MONTHLY P&L AT SCALE

### Costs

| Item | Monthly |
|------|---------|
| DeepSeek V4 Flash (70% of tasks) | $27 |
| DeepSeek R1 (20% of tasks) | $85 |
| Claude Sonnet Batch (10% of tasks) | $145 |
| Redis (caching) | $10 |
| VPS (orchestration) | $20 |
| X API (content flywheel) | $30 |
| Ollama local (electricity) | $15 |
| **Total** | **$332/month** |

### Revenue Scenarios

| Scenario | Findings/Month | Revenue | Profit | ROI |
|----------|---------------|---------|--------|-----|
| Bootstrapping | 1 medium | $500-$2K | $168-$1,668 | 50-500% |
| Growth | 3-4 mediums | $4.5K-$10K | $4,168-$9,668 | 1,200-2,900% |
| Strong | 6+ findings | $18K-$45K | $17,668-$44,668 | 5,300-13,400% |
| + Immunefi critical | 1 critical | +$10K-$100K+ | Life-changing | Infinite |

### Breakeven: 1 medium finding per month ($500-$3,000)

That covers all infrastructure costs with margin. Everything beyond is profit.

---

## THE COMPOUND FLYWHEEL

```
Enter EVERY contest on EVERY platform ($1-5 compute/contest)
                    │
                    ▼
Find bugs → Submit findings → Earn USDC
                    │
                    ▼
Leaderboard rank rises (automatic)
                    │
                    ▼
Twitter content from findings (automated, $30-50/mo)
                    │
                    ▼
Reputation compounds
                    │
                    ▼
Private audit inbound (protocols DM you)
    $300-$500/hr vs. diluted contest pools
                    │
                    ▼
Cantina/Spearbit fellowship ($12.5K-$20K/week)
                    │
                    ▼
Each private audit = portfolio piece = more reputation
                    │
                    └──→ feeds back to top ──→ COMPOUNDS
```

**Each contest is simultaneously:**
1. Revenue (prize pool earnings)
2. Marketing (leaderboard visibility)
3. Education (you improve with each codebase)
4. Portfolio (published findings = case studies)
5. Network (interact with judges, protocol teams, other auditors)

**The work IS the distribution. No other business has this property.**

---

## BUILD TIMELINE

| Week | Build | Ship |
|------|-------|------|
| 1 | Contest monitor daemon + auto-cloner + static analysis layer | Pipeline detects and clones contests |
| 2 | DeepSeek 5-agent analysis + LiteLLM router | Pipeline produces raw findings |
| 3 | Claude synthesis + Foundry PoC generation + validation | Pipeline produces validated reports |
| 4 | Submission automator (Playwright) + payment tracker | Pipeline submits to platforms |
| 5+ | Feedback loop + prompt tuning + continuous improvement | Pipeline improves itself |

**Total build time: 4 weeks to MVP autonomous pipeline.**

After that, the pipeline runs 24/7. Your role shifts from builder to:
- Reviewing flagged findings (30-60 min/contest)
- Tuning prompts based on feedback loop
- Engaging on Twitter for reputation
- Scaling to private audits as reputation compounds

---

## WHY THIS BEATS ALL 10 IDEAS

| Factor | SC Audit Pipeline | Others |
|--------|------------------|--------|
| Distribution | BUILT INTO PLATFORMS | Must build from scratch |
| CAC | $0 | $0.10-$50+ |
| Capital needed | $332/month | $0-$50K |
| Time to revenue | 4-6 weeks | Weeks to months |
| Google dependency | ZERO | Often high |
| Regulatory tailwind | MiCA makes audits mandatory | None |
| AI leverage | 10x speed advantage | Variable |
| Compound effect | Leaderboard → private inbound | Linear |
| Revenue ceiling | $500K-$1M+/year solo | Varies |
| Reversibility | HIGH | Varies |
| Existing tools | MCP servers, Claude skills, SmartGuard | Must build |

---

*Compiled from 6 parallel research agents, 200+ web sources, platform documentation, and on-chain data. All payment mechanics verified against official platform docs. Revenue claims cross-referenced against leaderboard data and auditor case studies.*

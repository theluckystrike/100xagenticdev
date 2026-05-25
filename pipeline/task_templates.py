from __future__ import annotations

"""
Task Templates — Pre-built research task sets for common pipeline use cases.

Each preset returns a list of (tasks, synthesis_prompt) tuples, one per phase.
"""

from orchestrator import Task

# ── Available Presets ───────────────────────────────────────────────────────
PRESETS = {
    "crypto_research": "Deep research on crypto tokens/protocols",
    "market_scan": "Broad market opportunity scanning",
    "competitive_intel": "Competitive intelligence gathering",
    "sec_audit_recon": "Security audit reconnaissance",
    "code_review": "Distributed code review and analysis",
    "seo_research": "SEO and content strategy research",
    "domain_research": "Domain/asset research and valuation",
    "tech_deep_dive": "Technical deep dive on a topic",
}

SYSTEM_PROMPT_RESEARCH = (
    "You are an expert research analyst. Provide detailed, data-driven analysis. "
    "Include specific numbers, dates, and sources where possible. "
    "Structure your response with clear headers and bullet points. "
    "Be thorough but concise — no filler. Cite sources."
)

SYSTEM_PROMPT_SECURITY = (
    "You are a senior security researcher. Analyze with precision. "
    "Focus on exploitable vulnerabilities, not theoretical risks. "
    "Provide severity ratings (Critical/High/Medium/Low) and proof-of-concept ideas. "
    "Structure output as: Finding → Impact → PoC → Remediation."
)

SYSTEM_PROMPT_CODE = (
    "You are a senior software engineer. Analyze code for bugs, security issues, "
    "performance problems, and architectural concerns. Be specific about line numbers "
    "and provide concrete fix suggestions. No vague advice."
)


def build_preset_tasks(preset: str, num_agents: int = 20, topic: str = None) -> list:
    """
    Build task phases for a preset.
    Returns: list of (list[Task], synthesis_prompt) tuples.
    """
    builders = {
        "crypto_research": _build_crypto_research,
        "market_scan": _build_market_scan,
        "competitive_intel": _build_competitive_intel,
        "sec_audit_recon": _build_sec_audit_recon,
        "code_review": _build_code_review,
        "seo_research": _build_seo_research,
        "domain_research": _build_domain_research,
        "tech_deep_dive": _build_tech_deep_dive,
    }

    builder = builders.get(preset)
    if not builder:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(PRESETS.keys())}")

    return builder(num_agents, topic)


def _build_crypto_research(n: int, topic: str = None) -> list:
    """Multi-phase crypto token/protocol research pipeline."""
    target = topic or "DeFi protocols"

    # Phase 1: Broad research across multiple dimensions
    phase1_prompts = [
        f"Analyze the tokenomics of the top 20 {target} tokens. For each: supply schedule, inflation rate, burn mechanisms, staking yield, revenue accrual to token holders. Calculate P/S and P/E ratios where possible.",
        f"Map the competitive landscape of {target}. Who are the top 10 players by TVL, volume, and revenue? What are their moats? Where are the gaps?",
        f"Analyze on-chain metrics for {target}: TVL trends (30d/90d/1y), active addresses, transaction counts, fee revenue, protocol revenue. Which protocols are growing fastest?",
        f"Research governance and team quality for top {target} projects. Token distribution, VC backing, team backgrounds, governance activity, treasury size and management.",
        f"Analyze the risk landscape for {target}: smart contract audit history, exploit history, regulatory risk, centralization risk, oracle dependency, key person risk.",
        f"Research upcoming catalysts for {target} in the next 6 months: protocol upgrades, token unlocks, fee switch proposals, partnership announcements, mainnet launches.",
        f"Compare fee structures and revenue models across {target}. Who has the best unit economics? Which protocols actually generate sustainable revenue?",
        f"Analyze cross-chain dynamics for {target}: which chains are gaining/losing market share? Bridge activity, liquidity fragmentation, multi-chain deployment strategies.",
        f"Research the macro setup for {target}: correlation with BTC/ETH, sensitivity to rates, institutional adoption trends, regulatory developments, ETF flows.",
        f"Deep dive on the 3 most undervalued {target} tokens by P/S ratio. What's the bull case? What could 5-10x these?",
        f"Analyze user acquisition and retention for {target}: DAU/MAU trends, user growth rates, retention cohorts, acquisition cost estimates.",
        f"Research DeFi composability and integration depth for {target}: how many other protocols integrate with each? Network effects and switching costs.",
        f"Analyze the liquidity landscape for {target}: DEX vs CEX volume, market depth, slippage at various trade sizes, market maker relationships.",
        f"Research insider activity for {target}: team token movements, VC unlock schedules, whale wallet accumulation/distribution patterns.",
        f"Compare developer activity for {target}: GitHub commits, contributors, repo growth, developer grants, hackathon participation.",
        f"Analyze yield sustainability for {target}: where does yield come from? Organic vs subsidized? What happens when incentives end?",
        f"Research narrative and social momentum for {target}: Twitter/Discord growth, mindshare metrics, CT sentiment, conference presence.",
        f"Deep dive on failed/declining {target} projects: what went wrong? Lessons learned? Warning signs we can apply to current holdings?",
        f"Analyze the MEV landscape affecting {target}: sandwich attacks, arbitrage, liquidation bots. Which protocols are most/least affected?",
        f"Research insurance and risk management options for {target}: cover protocols, self-insurance mechanisms, hedging strategies.",
    ]

    phase1_tasks = [
        Task(
            task_id=f"crypto-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.7,
            metadata={"dimension": p.split(".")[0][:50]},
        )
        for i, p in enumerate(phase1_prompts[:n])
    ]

    phase1_synthesis = (
        f"You are synthesizing research from {n} parallel agents analyzing {target}. "
        "Create a comprehensive investment research report with:\n"
        "1. EXECUTIVE SUMMARY (top 5 findings)\n"
        "2. TOP PICKS (rank the 5 best opportunities with conviction scores 1-10)\n"
        "3. RISK MATRIX (categorize risks by probability × impact)\n"
        "4. CATALYST CALENDAR (upcoming events that could move prices)\n"
        "5. PORTFOLIO CONSTRUCTION (suggested allocation across picks)\n"
        "6. KEY METRICS TABLE (P/S, TVL, revenue, growth for top 10)\n"
        "Resolve any contradictions between agents. Flag low-confidence findings."
    )

    # Phase 2: Deep dive on top picks from Phase 1
    phase2_tasks = [
        Task(
            task_id="crypto-deep-1",
            prompt=(
                "Based on the research synthesis, do a deep financial model on the #1 pick. "
                "Build a DCF/comparable model with bull/base/bear scenarios. "
                "Include sensitivity analysis on key assumptions."
            ),
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=8192,
            temperature=0.3,
        ),
        Task(
            task_id="crypto-deep-2",
            prompt=(
                "Based on the research synthesis, do a deep technical analysis on the #1 pick. "
                "Smart contract architecture, security posture, upgrade mechanisms, "
                "dependencies, and technical risks."
            ),
            system_prompt=SYSTEM_PROMPT_SECURITY,
            max_tokens=8192,
            temperature=0.3,
        ),
        Task(
            task_id="crypto-deep-3",
            prompt=(
                "Based on the research synthesis, create a detailed entry/exit strategy. "
                "Optimal entry points, DCA schedule, position sizing, stop losses, "
                "take profit levels, and portfolio rebalancing triggers."
            ),
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.3,
        ),
    ]

    phase2_synthesis = (
        "Combine the deep-dive analyses into a final actionable investment thesis. "
        "Include: conviction level (1-10), position size recommendation, "
        "entry/exit strategy, key monitoring metrics, and kill criteria."
    )

    return [
        (phase1_tasks, phase1_synthesis),
        (phase2_tasks, phase2_synthesis),
    ]


def _build_market_scan(n: int, topic: str = None) -> list:
    """Broad market opportunity scanning."""
    target = topic or "AI/ML developer tools"

    prompts = [
        f"Map all VC-funded startups in {target} from the last 12 months. Funding amounts, investors, traction metrics.",
        f"Identify underserved niches in {target} where demand exceeds supply. Look for complaints in forums, HN, Reddit.",
        f"Analyze pricing models across {target}. Who's underpriced? Overpriced? What pricing innovations exist?",
        f"Research open-source alternatives in {target}. Which commercial products are most vulnerable to OSS disruption?",
        f"Analyze the developer experience of the top 5 {target} products. Onboarding friction, documentation quality, time-to-value.",
        f"Research acquisition targets in {target}. Which companies are likely acquirers? What valuations are realistic?",
        f"Analyze distribution channels in {target}. Who dominates organic search? Paid? Community? Partnerships?",
        f"Research API ecosystem dynamics in {target}. Who has the best API? Most integrations? Strongest developer community?",
        f"Identify {target} products with strong network effects or data moats. What makes them defensible?",
        f"Analyze churn patterns in {target}. Why do users leave? What are the top retention drivers?",
        f"Research emerging markets for {target}. Which geos are underserved? Where is adoption accelerating?",
        f"Map the talent landscape for {target}. Where are the best engineers? What skills are in shortage?",
        f"Analyze regulatory risks for {target}. Which regulations could disrupt or enable the market?",
        f"Research PLG (product-led growth) strategies in {target}. Who does it best? What are the key metrics?",
        f"Identify 'boring' but profitable opportunities in {target}. Unsexy problems with high willingness-to-pay.",
        f"Research the enterprise vs SMB split in {target}. Where is revenue concentrated? Where is growth?",
        f"Analyze technical architecture patterns in {target}. What's the dominant stack? What's emerging?",
        f"Research community dynamics in {target}. Discord servers, Slack groups, forums. Where is the energy?",
        f"Analyze platform risk in {target}. Who depends on AWS/GCP/Apple/Google? How fragile are these dependencies?",
        f"Research the 'jobs to be done' framework for {target}. What are users actually hiring these products for?",
    ]

    tasks = [
        Task(
            task_id=f"market-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.7,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        f"Synthesize market research from {n} agents into an opportunity map for {target}. "
        "Structure as:\n"
        "1. TOP 5 OPPORTUNITIES (ranked by potential × feasibility)\n"
        "2. MARKET MAP (visual representation of the landscape)\n"
        "3. COMPETITIVE DYNAMICS (who's winning and why)\n"
        "4. DISTRIBUTION PLAYBOOK (best go-to-market strategies)\n"
        "5. RISKS & MITIGATIONS\n"
        "6. NEXT STEPS (concrete actions to validate top opportunities)"
    )

    return [(tasks, synthesis)]


def _build_competitive_intel(n: int, topic: str = None) -> list:
    """Competitive intelligence gathering."""
    target = topic or "the company"

    prompts = [
        f"Analyze {target}'s product roadmap based on public communications, job postings, and patent filings.",
        f"Research {target}'s pricing strategy evolution over the last 2 years. Changes, experiments, positioning.",
        f"Map {target}'s tech stack from job postings, engineering blog posts, and conference talks.",
        f"Analyze {target}'s hiring patterns. What roles are they prioritizing? What does this signal about strategy?",
        f"Research {target}'s customer segments. Who are their biggest customers? NPS scores? Public case studies?",
        f"Analyze {target}'s marketing strategy. SEO positioning, paid spend estimates, content strategy.",
        f"Research {target}'s partnership ecosystem. Integrations, channel partners, strategic alliances.",
        f"Analyze {target}'s financial health. Revenue estimates, growth rate, profitability, fundraising history.",
        f"Research {target}'s weaknesses. Customer complaints, bad reviews, known technical limitations.",
        f"Map {target}'s organizational structure from LinkedIn data. Team sizes, reporting lines, key hires.",
    ]

    tasks = [
        Task(
            task_id=f"intel-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.5,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        f"Create a comprehensive competitive intelligence brief on {target}. "
        "Include: SWOT analysis, strategic assessment, vulnerability map, "
        "and recommended counter-strategies."
    )

    return [(tasks, synthesis)]


def _build_sec_audit_recon(n: int, topic: str = None) -> list:
    """Security audit reconnaissance — distributed vuln research."""
    target = topic or "the target codebase"

    prompts = [
        f"Research known vulnerability patterns in {target}'s technology stack. CVE database, exploit-db, GitHub advisories.",
        f"Analyze {target}'s authentication and authorization architecture for common weaknesses (IDOR, privilege escalation, session management).",
        f"Research {target}'s input validation patterns. Look for SQL injection, XSS, command injection, path traversal vectors.",
        f"Analyze {target}'s cryptographic implementations. Weak algorithms, hardcoded keys, improper random number generation.",
        f"Research {target}'s dependency tree for known vulnerable packages. Focus on transitive dependencies.",
        f"Analyze {target}'s API surface for BOLA, rate limiting issues, mass assignment, and excessive data exposure.",
        f"Research {target}'s error handling for information disclosure. Stack traces, debug endpoints, verbose errors.",
        f"Analyze {target}'s file handling for upload vulnerabilities, path traversal, SSRF, and deserialization issues.",
        f"Research {target}'s business logic for race conditions, TOCTOU bugs, and state management issues.",
        f"Analyze {target}'s infrastructure configuration for misconfigurations, exposed services, and default credentials.",
    ]

    tasks = [
        Task(
            task_id=f"sec-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_SECURITY,
            max_tokens=4096,
            temperature=0.3,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        "Compile all security findings into a structured audit report:\n"
        "1. CRITICAL FINDINGS (immediate action required)\n"
        "2. HIGH FINDINGS (fix within 7 days)\n"
        "3. MEDIUM FINDINGS (fix within 30 days)\n"
        "4. LOW FINDINGS (fix at convenience)\n"
        "5. INFORMATIONAL (best practices)\n"
        "For each finding: Description → Impact → PoC Steps → Remediation → CVSS Score"
    )

    return [(tasks, synthesis)]


def _build_code_review(n: int, topic: str = None) -> list:
    """Distributed code review."""
    target = topic or "the codebase"

    prompts = [
        f"Review {target} for correctness bugs. Off-by-one errors, null derefs, type confusion, logic errors.",
        f"Review {target} for performance issues. N+1 queries, unnecessary allocations, missing indexes, blocking I/O.",
        f"Review {target} for security vulnerabilities. OWASP Top 10, injection, authentication bypasses.",
        f"Review {target} for code quality. Dead code, code duplication, overly complex functions, naming issues.",
        f"Review {target} for error handling. Swallowed exceptions, missing error paths, inconsistent error formats.",
    ]

    tasks = [
        Task(
            task_id=f"review-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_CODE,
            max_tokens=4096,
            temperature=0.3,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        "Merge all code review findings. Deduplicate, prioritize by severity, "
        "and provide a final APPROVE/REQUEST_CHANGES/BLOCK verdict with reasoning."
    )

    return [(tasks, synthesis)]


def _build_seo_research(n: int, topic: str = None) -> list:
    """SEO and content strategy research."""
    target = topic or "the website"

    prompts = [
        f"Analyze the top 20 ranking pages for {target}'s primary keywords. What do they have in common? Content structure, length, schema markup.",
        f"Research content gaps for {target}. What high-volume keywords are competitors ranking for that {target} is missing?",
        f"Analyze {target}'s backlink profile. Top linking domains, anchor text distribution, toxic links, opportunities.",
        f"Research {target}'s technical SEO health. Core Web Vitals, crawlability, indexation issues, canonical problems.",
        f"Analyze {target}'s competitor content strategies. Publishing frequency, content types, topic clusters.",
        f"Research featured snippet opportunities for {target}. Which queries trigger snippets? How to optimize for them?",
        f"Analyze {target}'s internal linking structure. Orphan pages, crawl depth, PageRank distribution.",
        f"Research {target}'s local SEO opportunities. Google Business Profile, local citations, review strategy.",
        f"Analyze emerging search trends relevant to {target}. AI overviews, voice search, visual search impacts.",
        f"Research {target}'s content refresh opportunities. Which existing pages could rank higher with updates?",
    ]

    tasks = [
        Task(
            task_id=f"seo-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.5,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        "Create a comprehensive SEO action plan:\n"
        "1. QUICK WINS (implement this week, high ROI)\n"
        "2. CONTENT ROADMAP (next 90 days, prioritized by traffic potential)\n"
        "3. TECHNICAL FIXES (prioritized by impact)\n"
        "4. LINK BUILDING STRATEGY\n"
        "5. MONITORING DASHBOARD METRICS"
    )

    return [(tasks, synthesis)]


def _build_domain_research(n: int, topic: str = None) -> list:
    """Domain/asset research and valuation."""
    target = topic or "premium domains"

    prompts = [
        f"Research recent {target} sales data. Comparable transactions, price trends, buyer profiles.",
        f"Analyze SEO metrics for {target}. Domain Authority, backlink profiles, organic traffic estimates.",
        f"Research brandability and memorability factors for {target}. Linguistic analysis, trademark conflicts.",
        f"Analyze monetization potential for {target}. Parking revenue, affiliate potential, development ROI.",
        f"Research market timing for {target}. Industry trends, seasonal patterns, optimal listing strategies.",
    ]

    tasks = [
        Task(
            task_id=f"domain-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_RESEARCH,
            max_tokens=4096,
            temperature=0.5,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        "Create a domain valuation report:\n"
        "1. ESTIMATED VALUE RANGE (low/mid/high with methodology)\n"
        "2. COMPARABLE SALES\n"
        "3. MONETIZATION ANALYSIS\n"
        "4. STRATEGIC BUYER TARGETS\n"
        "5. RECOMMENDED ACTION (hold/develop/sell)"
    )

    return [(tasks, synthesis)]


def _build_tech_deep_dive(n: int, topic: str = None) -> list:
    """Technical deep dive on a specific topic."""
    target = topic or "the technology"

    prompts = [
        f"Explain the core architecture of {target}. How does it work under the hood? Key design decisions.",
        f"Analyze {target}'s performance characteristics. Benchmarks, scaling behavior, resource consumption.",
        f"Compare {target} to its top 3 alternatives. Feature comparison, performance, developer experience.",
        f"Research {target}'s production deployment patterns. How do large companies use it? Common pitfalls.",
        f"Analyze {target}'s security model. Attack surface, known vulnerabilities, hardening best practices.",
        f"Research {target}'s ecosystem. Plugins, extensions, integrations, community tools.",
        f"Analyze {target}'s roadmap and future direction. Planned features, deprecations, breaking changes.",
        f"Research migration strategies for {target}. Moving to/from alternatives, data migration, downtime.",
        f"Deep dive on {target}'s internals. Data structures, algorithms, concurrency model, memory management.",
        f"Analyze {target}'s observability story. Logging, metrics, tracing, debugging tools.",
    ]

    tasks = [
        Task(
            task_id=f"tech-{i+1:02d}",
            prompt=p,
            system_prompt=SYSTEM_PROMPT_CODE,
            max_tokens=4096,
            temperature=0.5,
        )
        for i, p in enumerate(prompts[:n])
    ]

    synthesis = (
        f"Create a comprehensive technical assessment of {target}:\n"
        "1. ARCHITECTURE OVERVIEW (with diagram description)\n"
        "2. STRENGTHS & WEAKNESSES\n"
        "3. BEST USE CASES & ANTI-PATTERNS\n"
        "4. PRODUCTION READINESS SCORE (1-10)\n"
        "5. RECOMMENDED ADOPTION STRATEGY"
    )

    return [(tasks, synthesis)]

from __future__ import annotations

"""
Web Grounding — Async URL fetcher for live data injection into agent contexts.

Solves the core hallucination problem: agents fabricate intel because they
have no live data. This module fetches real URLs and strips them to clean text
that agents can use as grounded CONTEXT.

Usage:
    from web_grounding import fetch_grounding_context
    ctx = await fetch_grounding_context(urls, max_chars=8000)
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

MAX_URL_BYTES = 512_000       # 512KB raw HTML limit per URL
MAX_CHARS_PER_URL = 6_000     # extracted text chars per URL
MAX_TOTAL_CHARS = 40_000      # total context chars across all URLs
MAX_URLS = 20                 # max URLs per batch
FETCH_TIMEOUT_SEC = 20.0
MAX_CONCURRENT_FETCHES = 8


@dataclass
class FetchResult:
    """Result of fetching and extracting one URL."""
    url: str
    success: bool
    text: str = ""
    title: str = ""
    error: str = ""
    latency_ms: float = 0.0
    chars: int = 0


@dataclass
class GroundingContext:
    """Aggregated grounding context from multiple URLs."""
    results: list[FetchResult] = field(default_factory=list)
    total_chars: int = 0
    success_count: int = 0
    fail_count: int = 0

    def as_prompt_context(self) -> str:
        """Format as a CONTEXT block for injection into agent prompts."""
        assert self.results, "No results to format"
        sections = []
        for r in self.results:
            if r.success and r.text:
                sections.append(
                    f"=== SOURCE: {r.url} ===\n"
                    f"TITLE: {r.title}\n\n"
                    f"{r.text}"
                )
        if not sections:
            return "[No grounding data fetched — all URLs failed]"
        return "\n\n".join(sections)


def _html_to_text(html: str) -> tuple[str, str]:
    """
    Strip HTML to readable text. Returns (title, body_text).
    Removes scripts, styles, nav, footer noise.
    """
    assert isinstance(html, str), "html must be a string"

    # Extract title
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else ""

    # Remove noise tags
    for tag in ("script", "style", "nav", "footer", "header", "noscript", "iframe"):
        html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', ' ', html, flags=re.DOTALL | re.IGNORECASE)

    # Strip remaining tags
    text = re.sub(r'<[^>]{1,200}>', ' ', html)

    # Decode common HTML entities
    replacements = [
        ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
        ('&nbsp;', ' '), ('&quot;', '"'), ('&#39;', "'"),
        ('&ndash;', '–'), ('&mdash;', '—'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    assert isinstance(title, str), "title must be string"
    assert isinstance(text, str), "text must be string"
    return title, text


async def _fetch_one(
    url: str,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    max_chars: int,
) -> FetchResult:
    """Fetch one URL and extract text. Bounded by semaphore."""
    assert url.startswith(("http://", "https://")), f"Invalid URL scheme: {url}"
    assert max_chars > 0, "max_chars must be positive"

    t0 = time.monotonic()
    async with sem:
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

            raw = resp.text[:MAX_URL_BYTES // 2]  # char limit before HTML parse
            title, text = _html_to_text(raw)
            text = text[:max_chars]
            latency = (time.monotonic() - t0) * 1000

            return FetchResult(
                url=url,
                success=True,
                title=title[:200],
                text=text,
                latency_ms=latency,
                chars=len(text),
            )

        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return FetchResult(
                url=url,
                success=False,
                error=str(e)[:200],
                latency_ms=latency,
            )


async def fetch_grounding_context(
    urls: list[str],
    max_chars_per_url: int = MAX_CHARS_PER_URL,
    max_total_chars: int = MAX_TOTAL_CHARS,
    timeout_sec: float = FETCH_TIMEOUT_SEC,
) -> GroundingContext:
    """
    Fetch multiple URLs concurrently. Return GroundingContext.
    Bounded: max 20 URLs, 8 concurrent, 512KB raw per URL.
    """
    assert isinstance(urls, list), "urls must be a list"
    assert len(urls) <= MAX_URLS, f"Too many URLs: {len(urls)} > {MAX_URLS}"
    assert max_total_chars > 0, "max_total_chars must be positive"

    # Filter to valid HTTP URLs
    valid_urls = [u for u in urls[:MAX_URLS] if isinstance(u, str) and u.startswith("http")]

    ctx = GroundingContext()
    if not valid_urls:
        return ctx

    sem = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"},
        timeout=httpx.Timeout(timeout_sec, connect=8.0),
        follow_redirects=True,
    ) as client:
        tasks = [_fetch_one(u, client, sem, max_chars_per_url) for u in valid_urls]
        results: list[FetchResult] = await asyncio.gather(*tasks, return_exceptions=False)

    total = 0
    for r in results:
        ctx.results.append(r)
        if r.success:
            ctx.success_count += 1
            total += r.chars
            ctx.total_chars = total
            if total >= max_total_chars:
                break
        else:
            ctx.fail_count += 1

    assert ctx.total_chars >= 0, "total_chars must be non-negative"
    return ctx


# ── Known Intel Sources for LLM Model Research ──────────────────────────────
LLM_INTEL_URLS: list[str] = [
    # Pricing
    "https://openrouter.ai/models",
    "https://api.deepseek.com/pricing",
    # Benchmarks
    "https://artificialanalysis.ai/leaderboards/models",
    "https://livecodebench.github.io/leaderboard.html",
    "https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard",
    # Hallucination
    "https://huggingface.co/spaces/hallucination-leaderboard/leaderboard",
]

from __future__ import annotations

"""
DeepSeek Async Client — High-throughput API client with rate limiting & cost tracking.
OpenAI-compatible endpoint. Designed for 20+ concurrent agents.

Pricing (V4 promo until May 31, 2026):
  - Cache Hit Input: $0.003625/M tokens
  - Cache Miss Input: $0.435/M tokens
  - Output: $0.87/M tokens
  - V4 Flash: $0.14/M input, $0.28/M output
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

# ── Pricing (USD per million tokens) ────────────────────────────────────────
PRICING = {
    "deepseek-chat": {"input": 0.435, "output": 0.87, "cache_hit": 0.003625},
    "deepseek-reasoner": {"input": 0.87, "output": 3.48, "cache_hit": 0.007250},
}

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MAX_RETRIES = 4
BASE_BACKOFF_SEC = 1.0
MAX_BACKOFF_SEC = 30.0
CIRCUIT_BREAKER_THRESHOLD = 3


@dataclass
class UsageStats:
    """Per-request token usage and cost."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_cost_usd: float = 0.0
    latency_ms: float = 0.0


@dataclass
class AgentStats:
    """Cumulative stats for one agent."""
    agent_id: str = ""
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    consecutive_failures: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cached_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    circuit_open: bool = False

    @property
    def avg_latency_ms(self) -> float:
        if self.requests_success == 0:
            return 0.0
        return self.total_latency_ms / self.requests_success

    @property
    def cache_hit_rate(self) -> float:
        total_input = self.total_prompt_tokens + self.total_cached_tokens
        if total_input == 0:
            return 0.0
        return self.total_cached_tokens / total_input


@dataclass
class PipelineStats:
    """Fleet-wide stats across all agents."""
    agents: dict = field(default_factory=dict)
    budget_limit_usd: float = 50.0
    start_time: float = 0.0

    @property
    def total_cost_usd(self) -> float:
        return sum(a.total_cost_usd for a in self.agents.values())

    @property
    def total_requests(self) -> int:
        return sum(a.requests_total for a in self.agents.values())

    @property
    def budget_remaining_usd(self) -> float:
        return max(0.0, self.budget_limit_usd - self.total_cost_usd)

    @property
    def budget_pct_used(self) -> float:
        if self.budget_limit_usd == 0:
            return 100.0
        return (self.total_cost_usd / self.budget_limit_usd) * 100

    def is_budget_exceeded(self) -> bool:
        return self.total_cost_usd >= self.budget_limit_usd

    def get_agent(self, agent_id: str) -> AgentStats:
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentStats(agent_id=agent_id)
        return self.agents[agent_id]


def _calc_cost(model: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int) -> float:
    """Calculate cost in USD for a single request."""
    rates = PRICING.get(model, PRICING["deepseek-chat"])
    uncached_input = max(0, prompt_tokens - cached_tokens)
    cost = (
        (uncached_input / 1_000_000) * rates["input"]
        + (cached_tokens / 1_000_000) * rates["cache_hit"]
        + (completion_tokens / 1_000_000) * rates["output"]
    )
    return round(cost, 8)


class DeepSeekClient:
    """Async DeepSeek API client with connection pooling, retries, and circuit breaker."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        max_concurrent: int = 20,
        budget_limit_usd: float = 50.0,
        timeout_sec: float = 120.0,
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        self.model = model
        self.timeout_sec = timeout_sec
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.stats = PipelineStats(budget_limit_usd=budget_limit_usd)
        self.stats.start_time = time.time()

        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=DEEPSEEK_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout_sec, connect=10.0),
                limits=httpx.Limits(
                    max_connections=50,
                    max_keepalive_connections=25,
                    keepalive_expiry=30.0,
                ),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat(
        self,
        messages: list[dict],
        agent_id: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> dict:
        """
        Send a chat completion request with retry, rate limiting, circuit breaker.
        Returns: {"content": str, "usage": UsageStats, "raw": dict}
        """
        agent_stats = self.stats.get_agent(agent_id)

        # Circuit breaker check
        if agent_stats.circuit_open:
            raise RuntimeError(f"Agent {agent_id} circuit breaker OPEN ({agent_stats.consecutive_failures} consecutive failures)")

        # Budget check
        if self.stats.is_budget_exceeded():
            raise RuntimeError(f"Budget exceeded: ${self.stats.total_cost_usd:.4f} / ${self.stats.budget_limit_usd:.2f}")

        # Build request
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        body = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(MAX_RETRIES):
            async with self._semaphore:
                try:
                    client = await self._get_client()
                    t0 = time.monotonic()
                    resp = await client.post("/chat/completions", json=body)
                    latency_ms = (time.monotonic() - t0) * 1000

                    if resp.status_code == 429:
                        # Rate limited — backoff and retry
                        retry_after = float(resp.headers.get("retry-after", BASE_BACKOFF_SEC * (2 ** attempt)))
                        wait = min(retry_after, MAX_BACKOFF_SEC)
                        await asyncio.sleep(wait)
                        last_error = f"Rate limited (429), retry {attempt + 1}"
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                    # Parse usage
                    usage_raw = data.get("usage", {})
                    prompt_tokens = usage_raw.get("prompt_tokens", 0)
                    completion_tokens = usage_raw.get("completion_tokens", 0)
                    cached_tokens = usage_raw.get("prompt_cache_hit_tokens", 0)
                    cost = _calc_cost(self.model, prompt_tokens, completion_tokens, cached_tokens)

                    usage = UsageStats(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        cached_tokens=cached_tokens,
                        total_cost_usd=cost,
                        latency_ms=latency_ms,
                    )

                    # Update agent stats
                    agent_stats.requests_total += 1
                    agent_stats.requests_success += 1
                    agent_stats.consecutive_failures = 0
                    agent_stats.total_prompt_tokens += prompt_tokens
                    agent_stats.total_completion_tokens += completion_tokens
                    agent_stats.total_cached_tokens += cached_tokens
                    agent_stats.total_cost_usd += cost
                    agent_stats.total_latency_ms += latency_ms

                    content = ""
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")

                    return {"content": content, "usage": usage, "raw": data}

                except httpx.HTTPStatusError as e:
                    if e.response.status_code in (500, 502, 503):
                        wait = min(BASE_BACKOFF_SEC * (2 ** attempt), MAX_BACKOFF_SEC)
                        await asyncio.sleep(wait)
                        last_error = f"Server error {e.response.status_code}, retry {attempt + 1}"
                        continue
                    raise

                except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout) as e:
                    wait = min(BASE_BACKOFF_SEC * (2 ** attempt), MAX_BACKOFF_SEC)
                    await asyncio.sleep(wait)
                    last_error = f"{type(e).__name__}, retry {attempt + 1}"
                    continue

        # All retries exhausted
        agent_stats.requests_total += 1
        agent_stats.requests_failed += 1
        agent_stats.consecutive_failures += 1
        if agent_stats.consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            agent_stats.circuit_open = True

        raise RuntimeError(f"Agent {agent_id} failed after {MAX_RETRIES} retries: {last_error}")

    async def chat_multi_turn(
        self,
        initial_messages: list[dict],
        agent_id: str = "default",
        system_prompt: Optional[str] = None,
        max_turns: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stop_condition: Optional[callable] = None,
    ) -> list[dict]:
        """
        Multi-turn conversation. Returns list of all assistant responses.
        stop_condition: callable(content) -> bool, stops if True.
        """
        messages = list(initial_messages)
        responses = []

        for turn in range(max_turns):
            result = await self.chat(
                messages=messages,
                agent_id=agent_id,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = result["content"]
            responses.append(result)
            messages.append({"role": "assistant", "content": content})

            if stop_condition and stop_condition(content):
                break

        return responses

    def print_stats(self):
        """Print fleet-wide statistics."""
        elapsed = time.time() - self.stats.start_time
        print(f"\n{'='*60}")
        print(f"PIPELINE STATS — {elapsed:.1f}s elapsed")
        print(f"{'='*60}")
        print(f"Total cost:    ${self.stats.total_cost_usd:.6f} / ${self.stats.budget_limit_usd:.2f} ({self.stats.budget_pct_used:.1f}%)")
        print(f"Total requests: {self.stats.total_requests}")
        print(f"{'─'*60}")

        for aid, a in sorted(self.stats.agents.items()):
            status = "OPEN" if a.circuit_open else "OK"
            print(
                f"  Agent {aid:>3}: {a.requests_success}/{a.requests_total} ok | "
                f"${a.total_cost_usd:.6f} | "
                f"{a.avg_latency_ms:.0f}ms avg | "
                f"cache {a.cache_hit_rate:.0%} | "
                f"[{status}]"
            )
        print(f"{'='*60}\n")

    def stats_to_dict(self) -> dict:
        """Export stats as serializable dict."""
        return {
            "elapsed_sec": time.time() - self.stats.start_time,
            "total_cost_usd": self.stats.total_cost_usd,
            "budget_limit_usd": self.stats.budget_limit_usd,
            "budget_pct_used": self.stats.budget_pct_used,
            "total_requests": self.stats.total_requests,
            "agents": {
                aid: {
                    "requests_total": a.requests_total,
                    "requests_success": a.requests_success,
                    "requests_failed": a.requests_failed,
                    "total_cost_usd": a.total_cost_usd,
                    "avg_latency_ms": a.avg_latency_ms,
                    "cache_hit_rate": a.cache_hit_rate,
                    "circuit_open": a.circuit_open,
                }
                for aid, a in self.stats.agents.items()
            },
        }

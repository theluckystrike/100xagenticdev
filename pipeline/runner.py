#!/usr/bin/env python3
from __future__ import annotations

"""
Pipeline Runner — CLI entry point for the 35-agent pipeline.

Usage:
    python3 runner.py --preset llm_model_intel --agents 35 --anti-hallucination
    python3 runner.py --preset crypto_research --agents 35 --model flash
    python3 runner.py --prompt "Research X" --fan-out 35
    python3 runner.py --tasks my_tasks.json --model mimo --provider openrouter
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add pipeline dir to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import Orchestrator, Task
from task_templates import PRESETS, build_preset_tasks


def parse_args():
    p = argparse.ArgumentParser(
        description="100x Agentic Pipeline — 35 agents, MiMo V2.5 Pro, anti-hallucination"
    )
    p.add_argument("--tasks",   type=str, help="Path to tasks JSON file")
    p.add_argument("--preset",  type=str, choices=list(PRESETS.keys()),
                   help="Use a built-in task preset")
    p.add_argument("--prompt",  type=str, help="Single prompt to fan out across N agents")
    p.add_argument("--topic",   type=str, default="", help="Topic override for presets")
    p.add_argument("--fan-out", type=int, default=35,
                   help="Parallel agent variants for --prompt mode (default: 35)")
    p.add_argument("--agents",  type=int, default=35,
                   help="Max concurrent agents (default: 35)")
    p.add_argument("--model",   type=str, default="deepseek-chat",
                   help="Model alias or ID. Aliases: mimo, flash, pro, sonnet, haiku "
                        "(default: deepseek-chat)")
    p.add_argument("--provider", type=str, choices=["deepseek", "openrouter"], default=None,
                   help="API provider. Auto-detected from model if not set.")
    p.add_argument("--anti-hallucination", action="store_true",
                   help="Enable AH mode: MiMo V2.5 Pro, temp=0.1, citation required, "
                        "[UNVERIFIED] stripped")
    # ── Edge engine (niche scan → edge loop → verify → cards) ────────────────
    p.add_argument("--edge-loop", action="store_true",
                   help="Run the EDGE engine: niche-aware scan → iterative edge "
                        "loop → adversarial verify → ranked edge cards. Needs --topic.")
    p.add_argument("--load", type=str, default=None,
                   help="Launch a saved pipeline from a JSON config (topic+goal+"
                        "workflow). One command: --load pipelines/my_pipeline.json")
    p.add_argument("--niche", type=str, default=None,
                   help="Force a niche (else auto-classified). One of: crypto_defi, "
                        "equities_smallcap, devtools_saas, security_audit, seo_growth, "
                        "llm_ai_models, generic")
    p.add_argument("--rounds", type=int, default=3,
                   help="Edge-loop refinement rounds (default 3, max 8)")
    p.add_argument("--edge-threshold", type=float, default=0.6,
                   help="Min edge score to keep a candidate (0..1, default 0.6)")
    p.add_argument("--top-k-drill", type=int, default=4,
                   help="How many top candidates to drill deeper each round (default 4)")
    p.add_argument("--verify-confidence", type=float, default=0.5,
                   help="Min skeptic confidence for an edge to survive verify "
                        "(0..1, default 0.5; lower = more permissive)")
    p.add_argument("--no-enrich", action="store_true",
                   help="Skip the LLM step that adds topic-specific edge vectors")
    p.add_argument("--no-ground", action="store_true",
                   help="Disable live web grounding (scan from model memory only)")
    p.add_argument("--slug", type=str, default="",
                   help="Ticker/slug for niche seed URLs (e.g. UPST, hyperliquid)")
    p.add_argument("--ground-url", action="append", default=[], dest="ground_urls",
                   help="Explicit grounding URL to fetch (repeatable)")
    p.add_argument("--budget",      type=float, default=10.0,
                   help="Budget limit USD (default: 10.0)")
    p.add_argument("--output",      type=str,   default="",
                   help="Output directory (auto-generated if empty)")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tokens",  type=int,   default=4096)
    p.add_argument("--json-mode",   action="store_true")
    p.add_argument("--dry-run",     action="store_true",
                   help="Preview tasks without executing")
    return p.parse_args()


def load_tasks_from_file(filepath: str) -> list[dict]:
    """Load tasks from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if "phases" in data:
        return data["phases"]
    if "tasks" in data:
        return [{"tasks": data["tasks"]}]
    raise ValueError(f"Unrecognized tasks file format: {filepath}")


def build_fan_out_tasks(prompt: str, n: int, temperature: float, max_tokens: int) -> list[Task]:
    """Create N variant tasks from a single prompt for diverse coverage."""
    perspectives = [
        "Focus on quantitative data, numbers, and statistics.",
        "Focus on qualitative analysis, trends, and narratives.",
        "Focus on risks, threats, and failure modes.",
        "Focus on opportunities, upside, and growth potential.",
        "Focus on competitive landscape and market dynamics.",
        "Focus on technical architecture and implementation details.",
        "Focus on historical precedents and analogies.",
        "Focus on regulatory, legal, and compliance aspects.",
        "Focus on user experience, adoption, and market fit.",
        "Focus on financial modeling, unit economics, and valuation.",
        "Focus on contrarian views and underexplored angles.",
        "Focus on supply chain, dependencies, and infrastructure.",
        "Focus on team, leadership, and organizational dynamics.",
        "Focus on timeline, milestones, and execution risk.",
        "Focus on adjacent markets and cross-domain opportunities.",
        "Focus on moats, defensibility, and long-term durability.",
        "Focus on distribution channels and go-to-market strategy.",
        "Focus on technology stack and scalability.",
        "Focus on ecosystem, partnerships, and network effects.",
        "Focus on macro trends, geopolitics, and systemic risk.",
    ]

    tasks = []
    for i in range(min(n, len(perspectives))):
        tasks.append(Task(
            task_id=f"fan-{i+1:02d}",
            prompt=f"{prompt}\n\n{perspectives[i]}",
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={"perspective": perspectives[i]},
        ))
    return tasks


def print_task_summary(phases_data: list, dry_run: bool = False):
    """Print a summary of tasks to be executed."""
    total = sum(len(p.get("tasks", [])) if isinstance(p, dict) else len(p) for p in phases_data)
    label = "DRY RUN — " if dry_run else ""
    print(f"\n{label}Pipeline Summary:")
    print(f"  Phases: {len(phases_data)}")
    print(f"  Total tasks: {total}")
    for i, phase in enumerate(phases_data, 1):
        tasks = phase.get("tasks", []) if isinstance(phase, dict) else phase
        print(f"  Phase {i}: {len(tasks)} tasks")
        for j, t in enumerate(tasks[:3]):
            preview = (t.get("prompt", "") if isinstance(t, dict) else getattr(t, "prompt", ""))[:60]
            print(f"    [{j+1}] {preview}...")
        if len(tasks) > 3:
            print(f"    ... and {len(tasks) - 3} more")
    print()


def _build_dry_run_phases(args) -> list:
    """Build task list from args for dry-run preview without initializing client."""
    from task_templates import build_preset_tasks
    if args.preset:
        return build_preset_tasks(args.preset, num_agents=args.agents, topic=args.topic or None)
    if args.prompt:
        tasks = build_fan_out_tasks(args.prompt, args.fan_out, args.temperature, args.max_tokens)
        return [(tasks, None)]
    return []


async def run_edge_loop(args):
    """Run the edge engine end-to-end (or preview it on --dry-run)."""
    import context_scanner as cs
    if not args.topic:
        print("Error: --edge-loop requires --topic")
        sys.exit(1)

    if args.dry_run:
        profile = cs.build_profile(args.topic, niche=args.niche)
        print(f"\nDRY RUN — EDGE engine plan for: {args.topic}")
        print(f"  Niche: {profile.niche}  (matched: {profile.matched_keywords})")
        print(f"  Rounds: {args.rounds} | Threshold: {args.edge_threshold} | "
              f"Drill top-{args.top_k_drill} | Enrich: {not args.no_enrich}")
        print(f"  Scan vectors ({len(profile.vectors)}):")
        for v in profile.vectors:
            print(f"    • {v.key}: {v.description}")
        return

    from edge_pipeline import EdgePipeline
    pipe = EdgePipeline(
        topic=args.topic, niche=args.niche, agents=args.agents, budget=args.budget,
        model=args.model, provider=args.provider, output_dir=args.output,
        rounds=args.rounds, threshold=args.edge_threshold,
        top_k_drill=args.top_k_drill, verify_confidence=args.verify_confidence,
        enrich=not args.no_enrich, max_tokens=args.max_tokens,
        ground=not args.no_ground, seed_urls=args.ground_urls, slug=args.slug,
        verbose=True,
    )
    report = await pipe.run()
    await pipe.close()
    print(f"\nEdge Brief: {pipe.output_dir / 'edge_brief.md'}")
    print(f"Cards: {len(report.get('cards', []))} | "
          f"Cost: ${report['stats']['cost']:.4f} | Niche: {report['niche']}")


async def main():
    args = parse_args()

    # Saved-pipeline launcher: one config file → full edge run
    if args.load:
        from pipeline_loader import load_config, run_config, preview_config
        cfg = load_config(args.load)
        if args.output:
            cfg["output"] = args.output  # CLI --output overrides config
        if args.dry_run:
            preview_config(cfg)
        else:
            await run_config(cfg)
        return

    # Edge engine takes its own path (scan → loop → verify → cards)
    if args.edge_loop:
        await run_edge_loop(args)
        return

    # Dry-run: preview tasks without initializing API client
    if args.dry_run:
        phases = _build_dry_run_phases(args)
        print_task_summary([{"tasks": t} for t, _ in phases], dry_run=True)
        print(f"  Model: {args.model} | Agents: {args.agents} | Budget: ${args.budget}")
        print(f"  Anti-hallucination: {args.anti_hallucination} | Provider: {args.provider or 'auto'}")
        return

    if args.anti_hallucination:
        print("[AH mode] MiMo V2.5 Pro • temp=0.1 • citations required • [UNVERIFIED] stripped")

    orch = Orchestrator(
        max_agents=args.agents,
        model=args.model,
        budget_limit_usd=args.budget,
        output_dir=args.output,
        verbose=True,
        anti_hallucination=args.anti_hallucination,
        provider=args.provider,
    )

    # Preflight: one cheap call decides whether the API is usable at all. Without
    # it an unusable account (dead key / zero prepaid balance) shows up as N
    # identical opaque agent failures minutes into the run.
    pre = await orch.client.preflight()
    if not pre["ok"]:
        print(f"\n  API PREFLIGHT FAILED: {pre['reason']}")
        print("  Aborting before spawning agents (no tokens spent).\n")
        await orch.client.close()
        return 2
    print(f"[preflight] {args.provider or 'deepseek'} API ok — {pre['reason']}")

    if args.tasks:
        # Load from file
        phases_data = load_tasks_from_file(args.tasks)
        for phase_data in phases_data:
            if isinstance(phase_data, dict):
                tasks = [
                    Task(
                        task_id=t.get("task_id", f"t-{i}"),
                        prompt=t["prompt"],
                        system_prompt=t.get("system_prompt", ""),
                        temperature=t.get("temperature", args.temperature),
                        max_tokens=t.get("max_tokens", args.max_tokens),
                        json_mode=t.get("json_mode", args.json_mode),
                        metadata=t.get("metadata", {}),
                    )
                    for i, t in enumerate(phase_data.get("tasks", []))
                ]
                synthesis = phase_data.get("synthesis_prompt")
            else:
                tasks = [Task(task_id=f"t-{i}", prompt=str(phase_data)) for i, _ in enumerate([phase_data])]
                synthesis = None
            orch.add_phase(tasks, synthesis_prompt=synthesis)

    elif args.preset:
        topic = args.topic or None
        phases = build_preset_tasks(args.preset, num_agents=args.agents, topic=topic)
        for phase_tasks, synthesis in phases:
            orch.add_phase(phase_tasks, synthesis_prompt=synthesis)

    elif args.prompt:
        # Fan-out mode
        tasks = build_fan_out_tasks(
            args.prompt, args.fan_out, args.temperature, args.max_tokens
        )
        orch.add_phase(
            tasks,
            synthesis_prompt=(
                "Synthesize the following research from multiple agents into a comprehensive, "
                "well-structured report. Deduplicate information, resolve contradictions, "
                "and highlight the most important findings. Structure with clear headers."
            ),
        )

    else:
        print("Error: Must provide --tasks, --preset, or --prompt")
        sys.exit(1)

    report = await orch.run()

    # Print final summary
    print(f"\nFinal Report: {orch.output_dir / 'pipeline_report.json'}")
    print(f"Total cost: ${report['cost']['total_cost_usd']:.6f}")
    print(f"Tasks: {report['pipeline']['tasks_by_status']}")


if __name__ == "__main__":
    asyncio.run(main())

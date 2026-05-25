#!/usr/bin/env python3
from __future__ import annotations

"""
Pipeline Runner — CLI entry point for the 20-agent DeepSeek pipeline.

Usage:
    python3 runner.py --tasks tasks.json --agents 20 --budget 10.0
    python3 runner.py --preset crypto_research --agents 20
    python3 runner.py --prompt "Research X" --fan-out 20
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
    p = argparse.ArgumentParser(description="100x DeepSeek Pipeline Runner")
    p.add_argument("--tasks", type=str, help="Path to tasks JSON file")
    p.add_argument("--preset", type=str, choices=list(PRESETS.keys()), help="Use a built-in task preset")
    p.add_argument("--prompt", type=str, help="Single prompt to fan out across N agents")
    p.add_argument("--fan-out", type=int, default=20, help="Number of parallel agent variants for --prompt mode")
    p.add_argument("--agents", type=int, default=20, help="Max concurrent agents (default: 20)")
    p.add_argument("--model", type=str, default="deepseek-chat", help="DeepSeek model (default: deepseek-chat)")
    p.add_argument("--budget", type=float, default=10.0, help="Budget limit in USD (default: 10.0)")
    p.add_argument("--output", type=str, default="", help="Output directory (auto-generated if empty)")
    p.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    p.add_argument("--max-tokens", type=int, default=4096, help="Max tokens per response (default: 4096)")
    p.add_argument("--json-mode", action="store_true", help="Request JSON output from model")
    p.add_argument("--dry-run", action="store_true", help="Show tasks without executing")
    p.add_argument("--topic", type=str, default="", help="Topic override for presets")
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


async def main():
    args = parse_args()

    orch = Orchestrator(
        max_agents=args.agents,
        model=args.model,
        budget_limit_usd=args.budget,
        output_dir=args.output,
        verbose=True,
    )

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

    if args.dry_run:
        print_task_summary(
            [{"tasks": p.tasks} for p in orch.phases],
            dry_run=True,
        )
        return

    report = await orch.run()

    # Print final summary
    print(f"\nFinal Report: {orch.output_dir / 'pipeline_report.json'}")
    print(f"Total cost: ${report['cost']['total_cost_usd']:.6f}")
    print(f"Tasks: {report['pipeline']['tasks_by_status']}")


if __name__ == "__main__":
    asyncio.run(main())

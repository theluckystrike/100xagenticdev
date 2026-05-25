from __future__ import annotations

"""
20-Agent Parallel Orchestrator — Fan-out/fan-in task execution via DeepSeek API.

Supports:
  - 20 concurrent agents (configurable)
  - Multi-phase pipelines (phase N output feeds phase N+1)
  - Per-agent budget caps and circuit breakers
  - Real-time progress reporting
  - Results aggregation with deduplication
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from deepseek_client import DeepSeekClient


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """A single unit of work for one agent."""
    task_id: str
    prompt: str
    system_prompt: str = ""
    phase: int = 1
    priority: int = 0  # higher = more important
    max_tokens: int = 4096
    temperature: float = 0.7
    json_mode: bool = False
    depends_on: list = field(default_factory=list)  # task_ids
    metadata: dict = field(default_factory=dict)
    # Filled after execution
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    error: str = ""
    agent_id: str = ""


@dataclass
class Phase:
    """A group of tasks that run in parallel, then feed into the next phase."""
    phase_num: int
    tasks: list  # list of Task
    synthesis_prompt: Optional[str] = None  # optional prompt to synthesize phase results
    synthesis_result: str = ""


class Orchestrator:
    """Manages 20 parallel DeepSeek agents across multiple phases."""

    def __init__(
        self,
        max_agents: int = 20,
        model: str = "deepseek-chat",
        budget_limit_usd: float = 50.0,
        output_dir: str = "",
        verbose: bool = True,
    ):
        self.max_agents = max_agents
        self.model = model
        self.budget_limit_usd = budget_limit_usd
        self.verbose = verbose

        # Output directory
        if not output_dir:
            ts = time.strftime("%Y%m%d_%H%M%S")
            output_dir = f"./results/run_{ts}"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Client
        self.client = DeepSeekClient(
            model=model,
            max_concurrent=max_agents,
            budget_limit_usd=budget_limit_usd,
        )

        # Task tracking
        self.all_tasks: list[Task] = []
        self.phases: list[Phase] = []
        self._progress_lock = asyncio.Lock()
        self._completed = 0
        self._total = 0

    def add_phase(self, tasks: list[Task], synthesis_prompt: Optional[str] = None) -> int:
        """Add a phase of parallel tasks. Returns phase number."""
        phase_num = len(self.phases) + 1
        for t in tasks:
            t.phase = phase_num
        phase = Phase(phase_num=phase_num, tasks=tasks, synthesis_prompt=synthesis_prompt)
        self.phases.append(phase)
        self.all_tasks.extend(tasks)
        return phase_num

    async def _execute_task(self, task: Task, context: str = "") -> Task:
        """Execute a single task on an agent."""
        agent_id = f"agent-{task.task_id}"
        task.agent_id = agent_id
        task.status = TaskStatus.RUNNING

        if self.verbose:
            self._log(f"[{agent_id}] START: {task.prompt[:80]}...")

        try:
            # Inject context from previous phases if available
            prompt = task.prompt
            if context:
                prompt = f"CONTEXT FROM PREVIOUS PHASE:\n{context}\n\n---\n\nTASK:\n{prompt}"

            messages = [{"role": "user", "content": prompt}]

            result = await self.client.chat(
                messages=messages,
                agent_id=agent_id,
                system_prompt=task.system_prompt,
                temperature=task.temperature,
                max_tokens=task.max_tokens,
                json_mode=task.json_mode,
            )

            task.result = result["content"]
            task.cost_usd = result["usage"].total_cost_usd
            task.latency_ms = result["usage"].latency_ms
            task.status = TaskStatus.SUCCESS

            if self.verbose:
                self._log(
                    f"[{agent_id}] DONE: ${task.cost_usd:.6f} | "
                    f"{task.latency_ms:.0f}ms | "
                    f"{len(task.result)} chars"
                )

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            if self.verbose:
                self._log(f"[{agent_id}] FAIL: {e}")

        async with self._progress_lock:
            self._completed += 1
            pct = (self._completed / self._total * 100) if self._total > 0 else 0
            if self.verbose:
                self._log(
                    f"Progress: {self._completed}/{self._total} ({pct:.0f}%) | "
                    f"Cost: ${self.client.stats.total_cost_usd:.6f}"
                )

        return task

    async def _run_phase(self, phase: Phase, prev_context: str = "") -> str:
        """Run all tasks in a phase concurrently, then optionally synthesize."""
        self._log(f"\n{'='*60}")
        self._log(f"PHASE {phase.phase_num}: {len(phase.tasks)} tasks, {self.max_agents} agents")
        self._log(f"{'='*60}")

        # Execute all tasks in parallel
        coros = [self._execute_task(t, context=prev_context) for t in phase.tasks]
        await asyncio.gather(*coros, return_exceptions=True)

        # Collect successful results
        successes = [t for t in phase.tasks if t.status == TaskStatus.SUCCESS]
        failures = [t for t in phase.tasks if t.status == TaskStatus.FAILED]

        self._log(
            f"Phase {phase.phase_num} complete: "
            f"{len(successes)} success, {len(failures)} failed"
        )

        # Save phase results
        phase_file = self.output_dir / f"phase_{phase.phase_num}_results.json"
        self._save_phase_results(phase, phase_file)

        # Synthesize if requested
        if phase.synthesis_prompt and successes:
            self._log(f"Synthesizing phase {phase.phase_num} results...")
            combined = "\n\n---\n\n".join(
                f"AGENT {t.task_id}:\n{t.result}" for t in successes
            )
            synth_prompt = (
                f"{phase.synthesis_prompt}\n\n"
                f"RESULTS FROM {len(successes)} AGENTS:\n\n{combined}"
            )

            # Use a dedicated synthesis agent
            try:
                synth_result = await self.client.chat(
                    messages=[{"role": "user", "content": synth_prompt}],
                    agent_id=f"synth-phase-{phase.phase_num}",
                    temperature=0.3,
                    max_tokens=8192,
                )
                phase.synthesis_result = synth_result["content"]

                # Save synthesis
                synth_file = self.output_dir / f"phase_{phase.phase_num}_synthesis.md"
                synth_file.write_text(phase.synthesis_result, encoding="utf-8")

                return phase.synthesis_result
            except Exception as e:
                self._log(f"Synthesis failed: {e}")

        # Return concatenated results as context for next phase
        return "\n\n".join(t.result for t in successes)

    async def run(self) -> dict:
        """Execute all phases sequentially, tasks within phases in parallel."""
        self._total = sum(len(p.tasks) for p in self.phases)
        self._completed = 0
        start = time.time()

        self._log(f"Pipeline starting: {len(self.phases)} phases, {self._total} tasks, {self.max_agents} agents")
        self._log(f"Model: {self.model} | Budget: ${self.budget_limit_usd:.2f}")
        self._log(f"Output: {self.output_dir}")

        context = ""
        for phase in self.phases:
            if self.client.stats.is_budget_exceeded():
                self._log("BUDGET EXCEEDED — halting pipeline")
                # Mark remaining tasks as skipped
                for t in phase.tasks:
                    if t.status == TaskStatus.PENDING:
                        t.status = TaskStatus.SKIPPED
                break

            context = await self._run_phase(phase, prev_context=context)

        elapsed = time.time() - start

        # Final stats
        self.client.print_stats()

        # Save final report
        report = self._build_report(elapsed)
        report_file = self.output_dir / "pipeline_report.json"
        report_file.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

        self._log(f"\nPipeline complete in {elapsed:.1f}s")
        self._log(f"Total cost: ${self.client.stats.total_cost_usd:.6f}")
        self._log(f"Results: {self.output_dir}")

        await self.client.close()
        return report

    def _build_report(self, elapsed: float) -> dict:
        """Build final JSON report."""
        tasks_by_status = {}
        for t in self.all_tasks:
            status = t.status.value
            tasks_by_status.setdefault(status, 0)
            tasks_by_status[status] += 1

        return {
            "pipeline": {
                "elapsed_sec": elapsed,
                "phases": len(self.phases),
                "total_tasks": len(self.all_tasks),
                "tasks_by_status": tasks_by_status,
                "model": self.model,
                "max_agents": self.max_agents,
            },
            "cost": self.client.stats_to_dict(),
            "tasks": [
                {
                    "task_id": t.task_id,
                    "phase": t.phase,
                    "status": t.status.value,
                    "prompt_preview": t.prompt[:100],
                    "result_length": len(t.result),
                    "cost_usd": t.cost_usd,
                    "latency_ms": t.latency_ms,
                    "error": t.error,
                }
                for t in self.all_tasks
            ],
            "phases": [
                {
                    "phase_num": p.phase_num,
                    "tasks_count": len(p.tasks),
                    "has_synthesis": bool(p.synthesis_prompt),
                    "synthesis_length": len(p.synthesis_result),
                }
                for p in self.phases
            ],
        }

    def _save_phase_results(self, phase: Phase, filepath: Path):
        """Save individual phase results to JSON."""
        data = {
            "phase": phase.phase_num,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "status": t.status.value,
                    "prompt": t.prompt,
                    "result": t.result,
                    "cost_usd": t.cost_usd,
                    "latency_ms": t.latency_ms,
                    "error": t.error,
                    "metadata": t.metadata,
                }
                for t in phase.tasks
            ],
        }
        filepath.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _log(self, msg: str):
        """Print with timestamp."""
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")

        # Also append to log file
        log_file = self.output_dir / "pipeline.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")

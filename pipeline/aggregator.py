from __future__ import annotations

"""
Results Aggregator — Collects, deduplicates, and synthesizes pipeline output.
Generates HTML dashboard with cost breakdown and quality metrics.
"""

import json
import time
from pathlib import Path
from typing import Optional


def load_run_results(results_dir: str) -> dict:
    """Load all results from a pipeline run directory."""
    path = Path(results_dir)

    report = {}
    report_file = path / "pipeline_report.json"
    if report_file.exists():
        report = json.loads(report_file.read_text(encoding="utf-8"))

    phases = []
    for phase_file in sorted(path.glob("phase_*_results.json")):
        phases.append(json.loads(phase_file.read_text(encoding="utf-8")))

    syntheses = {}
    for synth_file in sorted(path.glob("phase_*_synthesis.md")):
        phase_num = synth_file.stem.split("_")[1]
        syntheses[phase_num] = synth_file.read_text(encoding="utf-8")

    return {
        "report": report,
        "phases": phases,
        "syntheses": syntheses,
        "log": _load_log(path / "pipeline.log"),
    }


def _load_log(log_path: Path) -> list[str]:
    """Load pipeline log lines."""
    if not log_path.exists():
        return []
    return log_path.read_text(encoding="utf-8").strip().split("\n")


def generate_dashboard_html(results: dict, output_path: str) -> str:
    """Generate a comprehensive HTML dashboard from pipeline results."""
    report = results.get("report", {})
    phases = results.get("phases", [])
    syntheses = results.get("syntheses", {})
    log_lines = results.get("log", [])

    pipeline_info = report.get("pipeline", {})
    cost_info = report.get("cost", {})
    tasks = report.get("tasks", [])

    total_cost = cost_info.get("total_cost_usd", 0)
    budget = cost_info.get("budget_limit_usd", 0)
    elapsed = pipeline_info.get("elapsed_sec", 0)
    status_counts = pipeline_info.get("tasks_by_status", {})
    agents = cost_info.get("agents", {})

    # Build task rows
    task_rows = ""
    for t in tasks:
        status_class = {
            "success": "status-success",
            "failed": "status-failed",
            "skipped": "status-skipped",
        }.get(t.get("status", ""), "status-pending")

        task_rows += f"""
        <tr>
            <td>{t.get('task_id', '')}</td>
            <td>P{t.get('phase', '')}</td>
            <td><span class="{status_class}">{t.get('status', '')}</span></td>
            <td title="{_escape(t.get('prompt_preview', ''))}">{_escape(t.get('prompt_preview', '')[:50])}...</td>
            <td>${t.get('cost_usd', 0):.6f}</td>
            <td>{t.get('latency_ms', 0):.0f}ms</td>
            <td>{t.get('result_length', 0):,}</td>
            <td class="error">{_escape(t.get('error', '')[:50])}</td>
        </tr>"""

    # Build agent rows
    agent_rows = ""
    for aid, a in sorted(agents.items()):
        cb_status = '<span class="status-failed">OPEN</span>' if a.get("circuit_open") else '<span class="status-success">OK</span>'
        agent_rows += f"""
        <tr>
            <td>{aid}</td>
            <td>{a.get('requests_success', 0)}/{a.get('requests_total', 0)}</td>
            <td>${a.get('total_cost_usd', 0):.6f}</td>
            <td>{a.get('avg_latency_ms', 0):.0f}ms</td>
            <td>{a.get('cache_hit_rate', 0):.0%}</td>
            <td>{cb_status}</td>
        </tr>"""

    # Build synthesis sections
    synthesis_html = ""
    for phase_num, content in sorted(syntheses.items()):
        synthesis_html += f"""
        <div class="synthesis-section">
            <h3>Phase {phase_num} Synthesis</h3>
            <div class="synthesis-content">{_escape(content)}</div>
        </div>"""

    # Build log
    log_html = "\n".join(f"<div class='log-line'>{_escape(l)}</div>" for l in log_lines[-100:])

    budget_pct = (total_cost / budget * 100) if budget > 0 else 0
    success_count = status_counts.get("success", 0)
    total_count = sum(status_counts.values())
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>100x Pipeline Dashboard</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; }}
    .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
    h1 {{ font-size: 28px; color: #fff; margin-bottom: 4px; }}
    h2 {{ font-size: 20px; color: #8b8bff; margin: 24px 0 12px; }}
    h3 {{ font-size: 16px; color: #aaa; margin-bottom: 8px; }}
    .subtitle {{ color: #666; font-size: 14px; margin-bottom: 20px; }}

    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .kpi-card {{ background: #151520; border: 1px solid #252535; border-radius: 8px; padding: 16px; }}
    .kpi-label {{ font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: #fff; margin-top: 4px; }}
    .kpi-value.green {{ color: #4ade80; }}
    .kpi-value.red {{ color: #f87171; }}
    .kpi-value.blue {{ color: #60a5fa; }}
    .kpi-value.yellow {{ color: #facc15; }}

    .budget-bar {{ width: 100%; height: 8px; background: #252535; border-radius: 4px; margin-top: 8px; overflow: hidden; }}
    .budget-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
    .budget-fill.low {{ background: #4ade80; }}
    .budget-fill.mid {{ background: #facc15; }}
    .budget-fill.high {{ background: #f87171; }}

    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ background: #151520; color: #8b8bff; padding: 10px 8px; text-align: left; font-weight: 600; position: sticky; top: 0; }}
    td {{ padding: 8px; border-bottom: 1px solid #1a1a2a; }}
    tr:hover {{ background: #151520; }}

    .status-success {{ color: #4ade80; font-weight: 600; }}
    .status-failed {{ color: #f87171; font-weight: 600; }}
    .status-skipped {{ color: #facc15; font-weight: 600; }}
    .status-pending {{ color: #666; }}
    .error {{ color: #f87171; font-size: 11px; }}

    .synthesis-section {{ background: #151520; border: 1px solid #252535; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
    .synthesis-content {{ white-space: pre-wrap; font-family: 'SF Mono', monospace; font-size: 13px; line-height: 1.6; max-height: 600px; overflow-y: auto; }}

    .log-container {{ background: #0d0d12; border: 1px solid #252535; border-radius: 8px; padding: 12px; max-height: 400px; overflow-y: auto; font-family: 'SF Mono', monospace; font-size: 11px; }}
    .log-line {{ padding: 2px 0; color: #888; }}

    .tabs {{ display: flex; gap: 4px; margin-bottom: 16px; }}
    .tab {{ padding: 8px 16px; background: #151520; border: 1px solid #252535; border-radius: 6px 6px 0 0; cursor: pointer; color: #888; font-size: 13px; }}
    .tab.active {{ background: #1a1a2a; color: #8b8bff; border-bottom-color: #1a1a2a; }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
</style>
</head>
<body>
<div class="container">
    <h1>100x DeepSeek Pipeline Dashboard</h1>
    <div class="subtitle">
        Model: {pipeline_info.get('model', 'deepseek-chat')} |
        Agents: {pipeline_info.get('max_agents', 20)} |
        Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Cost</div>
            <div class="kpi-value {'green' if total_cost < budget * 0.5 else 'yellow' if total_cost < budget * 0.8 else 'red'}">${total_cost:.6f}</div>
            <div class="budget-bar">
                <div class="budget-fill {'low' if budget_pct < 50 else 'mid' if budget_pct < 80 else 'high'}" style="width: {min(budget_pct, 100):.0f}%"></div>
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 4px">{budget_pct:.1f}% of ${budget:.2f} budget</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Elapsed Time</div>
            <div class="kpi-value blue">{elapsed:.1f}s</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Success Rate</div>
            <div class="kpi-value {'green' if success_rate > 90 else 'yellow' if success_rate > 70 else 'red'}">{success_rate:.0f}%</div>
            <div style="font-size: 11px; color: #666; margin-top: 4px">{success_count}/{total_count} tasks</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Tasks</div>
            <div class="kpi-value">{total_count}</div>
            <div style="font-size: 11px; color: #666; margin-top: 4px">
                <span class="status-success">{status_counts.get('success', 0)}</span> ok /
                <span class="status-failed">{status_counts.get('failed', 0)}</span> fail /
                <span class="status-skipped">{status_counts.get('skipped', 0)}</span> skip
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Phases</div>
            <div class="kpi-value blue">{pipeline_info.get('phases', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Agents</div>
            <div class="kpi-value">{len(agents)}</div>
        </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
        <div class="tab active" onclick="showTab('tasks')">Tasks</div>
        <div class="tab" onclick="showTab('agents')">Agents</div>
        <div class="tab" onclick="showTab('synthesis')">Synthesis</div>
        <div class="tab" onclick="showTab('log')">Log</div>
    </div>

    <!-- Tasks Tab -->
    <div id="tab-tasks" class="tab-content active">
        <table>
            <thead>
                <tr><th>ID</th><th>Phase</th><th>Status</th><th>Prompt</th><th>Cost</th><th>Latency</th><th>Output</th><th>Error</th></tr>
            </thead>
            <tbody>{task_rows}</tbody>
        </table>
    </div>

    <!-- Agents Tab -->
    <div id="tab-agents" class="tab-content">
        <table>
            <thead>
                <tr><th>Agent</th><th>Success/Total</th><th>Cost</th><th>Avg Latency</th><th>Cache Hit</th><th>Circuit</th></tr>
            </thead>
            <tbody>{agent_rows}</tbody>
        </table>
    </div>

    <!-- Synthesis Tab -->
    <div id="tab-synthesis" class="tab-content">
        {synthesis_html if synthesis_html else '<p style="color:#666">No synthesis results yet.</p>'}
    </div>

    <!-- Log Tab -->
    <div id="tab-log" class="tab-content">
        <div class="log-container">{log_html}</div>
    </div>
</div>

<script>
function showTab(name) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


def _escape(text: str) -> str:
    """Escape HTML entities."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 aggregator.py <results_dir> [output.html]")
        sys.exit(1)

    results_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"{results_dir}/dashboard.html"

    results = load_run_results(results_dir)
    path = generate_dashboard_html(results, output_path)
    print(f"Dashboard generated: {path}")

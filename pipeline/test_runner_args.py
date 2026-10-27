"""Regression check: runner.py rejects non-positive agent, fan-out and budget values.

Run from any directory:  python pipeline/test_runner_args.py
Uses only the dry-run path, so it needs no API key and no extra packages.
"""

import os
import subprocess
import sys
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "runner.py"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

INVALID = [
    ["--preset", "market_scan", "--agents", "0"],
    ["--preset", "market_scan", "--agents", "-3"],
    ["--prompt", "hi", "--fan-out", "0"],
    ["--preset", "market_scan", "--budget", "0"],
    ["--preset", "market_scan", "--budget", "-1"],
]


def run_dry(args: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(RUNNER), *args, "--dry-run"]
    return subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=60)


def main() -> int:
    failures = 0
    for args in INVALID:
        result = run_dry(args)
        if result.returncode != 2 or "error" not in result.stderr:
            failures += 1
            print(f"FAIL {' '.join(args)}: exit={result.returncode} expected=2")
    valid = run_dry(["--preset", "market_scan", "--agents", "5"])
    if valid.returncode != 0 or "Total tasks: 5" not in valid.stdout:
        failures += 1
        print(f"FAIL market_scan --agents 5: exit={valid.returncode} expected 5 tasks")
    if failures == 0:
        print("PASS: invalid agent/fan-out/budget values rejected; valid dry run unchanged")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

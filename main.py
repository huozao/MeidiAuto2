"""Repository pipeline entrypoint.

Runs the production workflow steps in order, sharing a single data directory.
Designed for local runs and GitHub Actions.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PipelineStep:
    """A script step executed by the orchestrator."""

    filename: str
    required: bool = True


PIPELINE_STEPS: tuple[PipelineStep, ...] = (
    PipelineStep("020 Email download.py"),
    PipelineStep("021 Merge excel.py"),
    PipelineStep("030 Warehousing at home.py"),
    PipelineStep("032 Warehousing at out.py"),
    PipelineStep("033 list insertion.py"),
    PipelineStep("041 operation.py"),
    PipelineStep("042 Color display.py"),
    PipelineStep("050 mailtxt.py"),
    PipelineStep("051 Send an email.py"),
)

REQUIRED_ENV_KEYS: tuple[str, ...] = (
    "EMAIL_ADDRESS_QQ",
    "EMAIL_PASSWORD_QQ|EMAIL_PASSWOR_QQ",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MeidiAuto pipeline")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="shared output directory used by all steps (default: ./data)",
    )
    parser.add_argument(
        "--script-dir",
        default="script",
        help="directory containing step scripts (default: ./script)",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="stop pipeline immediately when a step fails",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the execution plan without running scripts",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate environment and step files only, then exit",
    )
    parser.add_argument(
        "--report-file",
        default="",
        help="optional JSON report path (relative to repo root if not absolute)",
    )
    return parser.parse_args()


def _has_env_group(value: str) -> bool:
    return any(os.getenv(k.strip()) for k in value.split("|"))


def check_environment() -> list[str]:
    missing: list[str] = []
    for key in REQUIRED_ENV_KEYS:
        if not _has_env_group(key):
            missing.append(key)
    return missing


def missing_step_files(script_dir: Path, steps: Iterable[PipelineStep]) -> list[str]:
    missing: list[str] = []
    for step in steps:
        if step.required and not (script_dir / step.filename).exists():
            missing.append(step.filename)
    return missing


def run_step(step: PipelineStep, script_dir: Path, data_dir: Path) -> tuple[bool, float]:
    script_path = script_dir / step.filename
    if not script_path.exists():
        msg = f"❌ Missing step script: {script_path}"
        if step.required:
            print(msg)
            return False, 0.0
        print(f"⚠️ {msg} (optional step skipped)")
        return True, 0.0

    cmd = [sys.executable, str(script_path), str(data_dir)]
    print(f"\n🚀 Running: {' '.join(cmd)}")
    started = time.time()
    completed = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - started

    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)

    if completed.returncode == 0:
        print(f"✅ Finished {step.filename} in {elapsed:.2f}s")
        return True, elapsed

    print(f"❌ Failed {step.filename} (exit={completed.returncode}) after {elapsed:.2f}s")
    return False, elapsed


def write_report(report_file: str, payload: dict, root: Path) -> None:
    if not report_file:
        return
    path = Path(report_file)
    if not path.is_absolute():
        path = (root / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"🧾 Report written to: {path}")


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    script_dir = (root / args.script_dir).resolve()
    data_dir = (root / args.data_dir).resolve()

    print(f"📁 Script directory: {script_dir}")
    print(f"📁 Data directory: {data_dir}")
    print(f"📋 Total steps: {len(PIPELINE_STEPS)}")

    if not script_dir.exists():
        print(f"❌ Script directory does not exist: {script_dir}")
        return 2

    missing_files = missing_step_files(script_dir, PIPELINE_STEPS)
    missing_env = check_environment()

    if args.dry_run:
        for index, step in enumerate(PIPELINE_STEPS, start=1):
            print(f"{index:02d}. {step.filename}")
        print("🧪 Dry run complete.")
        return 0

    if args.check:
        if missing_files:
            print(f"❌ Missing required step files: {', '.join(missing_files)}")
        else:
            print("✅ All required step files exist.")

        if missing_env:
            print(f"⚠️ Missing environment variables: {', '.join(missing_env)}")
        else:
            print("✅ Required environment variables are available.")

        return 0 if not missing_files else 1

    os.makedirs(data_dir, exist_ok=True)

    failures: list[str] = []
    total_time = 0.0
    started_at = time.strftime("%Y-%m-%d %H:%M:%S")

    for step in PIPELINE_STEPS:
        ok, elapsed = run_step(step, script_dir, data_dir)
        total_time += elapsed
        if not ok:
            failures.append(step.filename)
            if args.stop_on_error:
                break

    print("\n================ Pipeline Summary ================")
    success = not failures
    if failures:
        print(f"❌ Failed steps ({len(failures)}): {', '.join(failures)}")
        print(f"⏱️ Elapsed: {total_time:.2f}s")
    else:
        print("🎉 All steps completed successfully")
        print(f"⏱️ Elapsed: {total_time:.2f}s")

    write_report(
        args.report_file,
        {
            "started_at": started_at,
            "elapsed_seconds": round(total_time, 2),
            "success": success,
            "failed_steps": failures,
            "step_count": len(PIPELINE_STEPS),
            "data_dir": str(data_dir),
            "script_dir": str(script_dir),
        },
        root,
    )

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

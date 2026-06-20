#!/usr/bin/env python3
"""End-to-end script-to-voice pipeline wrapper."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_DIR / "config" / "defaults.json"


def slugify(value: str) -> str:
    value = re.sub(r"\.[^.]+$", "", Path(value).name)
    value = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff_-]+", "-", value).strip("-")
    return value[:80] or "script2voice"


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a script into complete audio.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--name", help="Run name under script2voice/runs/")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true", help="Only clean and segment the script.")
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--min-chars", type=int)
    parser.add_argument("--speed", type=float)
    parser.add_argument("--no-mp3", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_name = args.name or f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(str(args.input))}"
    run_dir = PROJECT_DIR / "runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    prepare_cmd = [
        sys.executable,
        str(PROJECT_DIR / "scripts" / "prepare_segments.py"),
        "--input",
        str(args.input),
        "--run-dir",
        str(run_dir),
        "--config",
        str(args.config),
    ]
    if args.max_chars:
        prepare_cmd += ["--max-chars", str(args.max_chars)]
    if args.min_chars:
        prepare_cmd += ["--min-chars", str(args.min_chars)]
    run(prepare_cmd)

    if args.dry_run:
        print(f"Dry run complete: {run_dir}")
        return

    cosy_python = cfg.get("cosyvoice_python") or sys.executable
    synth_cmd = [
        cosy_python,
        str(PROJECT_DIR / "scripts" / "synthesize_cosyvoice.py"),
        "--run-dir",
        str(run_dir),
        "--config",
        str(args.config),
    ]
    if args.speed is not None:
        synth_cmd += ["--speed", str(args.speed)]
    if args.no_mp3:
        synth_cmd.append("--no-mp3")
    run(synth_cmd)
    print(f"Done: {run_dir / 'audio' / 'final.wav'}")


if __name__ == "__main__":
    main()

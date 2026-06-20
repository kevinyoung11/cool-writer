#!/usr/bin/env python3
"""Check local dependencies for the script2voice CosyVoice pipeline."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
CONFIG = PROJECT_DIR / "config" / "defaults.json"


def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    checks = {
        "cosyvoice_root": Path(cfg["cosyvoice_root"]).exists(),
        "cosyvoice_python": Path(cfg["cosyvoice_python"]).exists(),
        "model_dir": Path(cfg["model_dir"]).exists(),
        "prompt_wav": Path(cfg["prompt_wav"]).exists(),
        "cache_dir_parent": Path(cfg["cache_dir"]).parent.exists(),
        "ffmpeg": shutil.which("ffmpeg") is not None,
    }
    for name, ok in checks.items():
        print(f"{'OK' if ok else 'MISSING'} {name}")
    if checks["cosyvoice_python"]:
        subprocess.run(
            [
                cfg["cosyvoice_python"],
                "-c",
                "import torch, torchaudio, modelscope; print('OK python imports')",
            ],
            check=False,
        )


if __name__ == "__main__":
    main()

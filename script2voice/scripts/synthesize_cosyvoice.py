#!/usr/bin/env python3
"""Synthesize prepared script segments with the local CosyVoice installation."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_DIR / "config" / "defaults.json"


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_only(value: str | None) -> set[int] | None:
    if not value:
        return None
    selected: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(x) for x in part.split("-", 1)]
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    return selected


def text_for_tts(text: str) -> str:
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def silence_wav(path: Path, ms: int, sample_rate: int) -> None:
    seconds = max(ms, 0) / 1000
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={sample_rate}:cl=mono",
            "-t",
            f"{seconds:.3f}",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def concat_wavs(parts: list[Path], output: Path) -> None:
    list_path = output.with_suffix(".concat.txt")
    list_path.write_text(
        "".join(f"file '{part.resolve()}'\n" for part in parts),
        encoding="utf-8",
    )
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(output)],
        check=True,
    )


def wav_to_mp3(wav: Path, mp3: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3)],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate wav/mp3 from prepared segments using CosyVoice.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--only", help="Segment ids to regenerate, e.g. 3,4,8-10")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--no-mp3", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    cosyvoice_root = Path(cfg["cosyvoice_root"])
    model_dir = Path(cfg["model_dir"])
    prompt_wav = Path(cfg["prompt_wav"])
    prompt_text = cfg["prompt_text"]
    cache_dir = Path(cfg.get("cache_dir", PROJECT_DIR / "cache"))
    speed = args.speed if args.speed is not None else float(cfg.get("speed", 1.0))
    sample_rate = int(cfg.get("sample_rate", 24000))
    pause_ms = int(cfg.get("pause_ms", 260))

    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MODELSCOPE_CACHE", str(cache_dir / "modelscope"))
    os.environ.setdefault("HF_HOME", str(cache_dir / "huggingface"))
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    sys.path.insert(0, str(cosyvoice_root))
    sys.path.append(str(cosyvoice_root / "third_party" / "Matcha-TTS"))

    from cosyvoice.cli.cosyvoice import AutoModel
    import torchaudio

    segments = json.loads((args.run_dir / "segments.json").read_text(encoding="utf-8"))
    selected = parse_only(args.only)

    audio_dir = args.run_dir / "audio"
    parts_dir = audio_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading CosyVoice model: {model_dir}")
    cosyvoice = AutoModel(model_dir=str(model_dir), fp16=False)
    print(f"Generating {len(segments) if selected is None else len(selected)} segment(s)")

    wav_paths: list[Path] = []
    generated: list[dict] = []
    for segment in segments:
        seg_id = int(segment["id"])
        wav_path = parts_dir / f"seg_{seg_id:03d}.wav"
        wav_paths.append(wav_path)
        if selected is not None and seg_id not in selected:
            if not wav_path.exists():
                raise SystemExit(f"Missing existing wav for skipped segment {seg_id}: {wav_path}")
            continue

        text = text_for_tts(segment["text"])
        if not text:
            continue
        print(f"[{seg_id:03d}] {text[:80]}")
        outputs = cosyvoice.inference_zero_shot(
            text,
            prompt_text,
            str(prompt_wav),
            stream=False,
            speed=speed,
            text_frontend=True,
        )
        saved = False
        for result in outputs:
            torchaudio.save(str(wav_path), result["tts_speech"], cosyvoice.sample_rate)
            saved = True
            break
        if not saved:
            raise RuntimeError(f"CosyVoice produced no audio for segment {seg_id}")
        generated.append({"id": seg_id, "wav": str(wav_path), "text": text})

    if selected is not None:
        print("Partial regeneration complete. Reassembling full audio from existing parts.")

    missing = [p for p in wav_paths if not p.exists()]
    if missing:
        raise SystemExit("Missing wav part(s):\n" + "\n".join(str(p) for p in missing))

    final_parts: list[Path] = []
    silence_path = audio_dir / f"silence_{pause_ms}ms.wav"
    silence_wav(silence_path, pause_ms, sample_rate)
    for idx, wav in enumerate(wav_paths):
        final_parts.append(wav)
        if idx != len(wav_paths) - 1:
            final_parts.append(silence_path)

    final_wav = audio_dir / "final.wav"
    concat_wavs(final_parts, final_wav)
    if not args.no_mp3:
        wav_to_mp3(final_wav, audio_dir / "final.mp3")

    (args.run_dir / "synthesis_manifest.json").write_text(
        json.dumps(
            {
                "run_dir": str(args.run_dir),
                "segments": len(segments),
                "generated": generated,
                "final_wav": str(final_wav),
                "final_mp3": str(audio_dir / "final.mp3") if not args.no_mp3 else None,
                "speed": speed,
                "pause_ms": pause_ms,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Generated: {final_wav}")
    if not args.no_mp3:
        print(f"Generated: {audio_dir / 'final.mp3'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Prepare a normal Markdown/text script for CosyVoice batch synthesis."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_DIR / "config" / "defaults.json"


@dataclass
class Segment:
    id: int
    text: str
    chars: int
    notes: str = ""


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_main_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n")
    text = re.sub(r"```.*?```", "", text, flags=re.S)

    # Prefer common body sections if present.
    body_markers = ["## 正片口播", "## 正片", "## 2. 可直接复制到 TTS 的分段文本"]
    for marker in body_markers:
        if marker in text:
            text = text.split(marker, 1)[1]
            break

    stop_markers = [
        "\n## 片尾字幕",
        "\n## 置顶评论",
        "\n## 可直接放置顶",
        "\n## 3. 后期",
        "\n## 后期",
        "\n## 拍摄备注",
    ]
    for marker in stop_markers:
        if marker in text:
            text = text.split(marker, 1)[0]

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith(">"):
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            continue
        if re.match(r"^[-*]\s+", stripped):
            stripped = re.sub(r"^[-*]\s+", "", stripped)
        stripped = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", stripped)
        stripped = re.sub(r"\[[^\]]+\]\([^)]*\)", "", stripped)
        stripped = stripped.replace("**", "").replace("__", "").replace("`", "")
        stripped = re.sub(r"^\[[^\]]+\]$", "", stripped)
        if stripped:
            lines.append(stripped)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def split_sentences(text: str) -> list[str]:
    parts: list[str] = []
    for para in re.split(r"\n+", text):
        para = para.strip()
        if not para:
            continue
        bits = re.split(r"(?<=[。！？!?；;])", para)
        for bit in bits:
            bit = bit.strip()
            if bit:
                parts.append(bit)
    return parts


def split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]
    chunks: list[str] = []
    buf = ""
    for piece in re.split(r"(?<=[，,、：:])", sentence):
        piece = piece.strip()
        if not piece:
            continue
        if len(buf) + len(piece) <= max_chars:
            buf += piece
        else:
            if buf:
                chunks.append(buf)
            if len(piece) > max_chars:
                for i in range(0, len(piece), max_chars):
                    chunks.append(piece[i : i + max_chars])
                buf = ""
            else:
                buf = piece
    if buf:
        chunks.append(buf)
    return chunks


def make_segments(text: str, max_chars: int, min_chars: int) -> list[Segment]:
    sentences: list[str] = []
    for sentence in split_sentences(text):
        sentences.extend(split_long_sentence(sentence, max_chars))

    chunks: list[str] = []
    buf = ""
    for sentence in sentences:
        candidate = f"{buf}{sentence}" if not buf else f"{buf}\n{sentence}"
        if len(candidate) <= max_chars or len(buf) < min_chars:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            buf = sentence
    if buf:
        chunks.append(buf)

    if len(chunks) >= 2 and len(chunks[-1]) < min_chars:
        merged = f"{chunks[-2]}\n{chunks[-1]}"
        if len(merged) <= max_chars + min_chars:
            chunks[-2] = merged
            chunks.pop()

    return [Segment(id=i + 1, text=chunk.strip(), chars=len(chunk.strip())) for i, chunk in enumerate(chunks)]


def write_outputs(run_dir: Path, cleaned: str, segments: list[Segment]) -> None:
    seg_dir = run_dir / "segments"
    if seg_dir.exists():
        shutil.rmtree(seg_dir)
    seg_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "cleaned_script.txt").write_text(cleaned + "\n", encoding="utf-8")
    (run_dir / "segments.json").write_text(
        json.dumps([asdict(s) for s in segments], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_lines = ["id\tchars\tfile\ttext"]
    for seg in segments:
        filename = f"seg_{seg.id:03d}.txt"
        (seg_dir / filename).write_text(seg.text + "\n", encoding="utf-8")
        one_line = seg.text.replace("\n", " ")
        manifest_lines.append(f"{seg.id}\t{seg.chars}\tsegments/{filename}\t{one_line}")
    (run_dir / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and segment a script for TTS.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--min-chars", type=int)
    args = parser.parse_args()

    cfg = load_config(args.config)
    max_chars = args.max_chars or int(cfg.get("max_chars", 95))
    min_chars = args.min_chars or int(cfg.get("min_chars", 18))

    raw = args.input.read_text(encoding="utf-8")
    cleaned = extract_main_text(raw)
    if not cleaned:
        raise SystemExit("No speakable text found after cleaning.")

    segments = make_segments(cleaned, max_chars=max_chars, min_chars=min_chars)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(args.run_dir, cleaned, segments)
    print(f"Prepared {len(segments)} segment(s) in {args.run_dir}")


if __name__ == "__main__":
    main()

"""Real figure generation for the article-publisher skill.

Environment reality (probed): no text-to-image backend and no API key, but
Google Chrome is installed. So we generate the *deterministic* figures a
methodology article needs — flow chains, two-column comparisons, simple tables
— as clean SVG, then render them to real PNG via Chrome headless. These are
content-determined diagrams (not creative art), so deterministic rendering is
exactly right.

Creative images (cover/illustration) need a text-to-image model; without one we
do NOT fake them — they stay as prompts in media-plan.json and the executor
reports them as `deferred` so the checklist flags them for manual generation.

media-plan.json asset shape consumed here:
  "figure-x": {
     "type": "figure",
     "diagram": {
        "kind": "flow" | "compare" | "table",
        "title": "...",
        ...kind-specific fields...
     },
     "output": "assets/figure-x.png"
  }
  "cover": { "type": "image", "executor": "manual_or_existing", "prompt": "..." }
"""

from __future__ import annotations

import html
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

# palette (cool, clean, not flashy — matches the cover brief)
BG = "#f5f7fa"
INK = "#1a2233"
ACCENT = "#2f6df0"
MUTED = "#6b7787"
BOX = "#ffffff"
LINE = "#c7d0db"
FONT = "-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif"


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _wrap(text: str, width: int) -> list[str]:
    # naive CJK-aware wrap by character count
    out, line = [], ""
    for ch in text:
        line += ch
        if len(line) >= width:
            out.append(line)
            line = ""
    if line:
        out.append(line)
    return out or [""]


def svg_flow(title: str, steps: list[str]) -> str:
    pad, bw, bh, gap = 40, 150, 64, 36
    cols = len(steps)
    w = pad * 2 + cols * bw + (cols - 1) * gap
    h = 180
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
        f'<text x="{w/2}" y="44" font-size="22" font-weight="700" '
        f'text-anchor="middle" fill="{INK}" font-family="{FONT}">{_esc(title)}</text>',
    ]
    y = 90
    for i, step in enumerate(steps):
        x = pad + i * (bw + gap)
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" '
                     f'fill="{BOX}" stroke="{LINE}" stroke-width="1.5"/>')
        lines = _wrap(step, 6)
        ly = y + bh / 2 - (len(lines) - 1) * 11 + 5
        for ln in lines:
            parts.append(f'<text x="{x+bw/2}" y="{ly}" font-size="16" '
                         f'text-anchor="middle" fill="{INK}" '
                         f'font-family="{FONT}">{_esc(ln)}</text>')
            ly += 22
        if i < cols - 1:
            ax = x + bw + gap / 2
            parts.append(f'<path d="M{x+bw} {y+bh/2} L{x+bw+gap} {y+bh/2}" '
                         f'stroke="{ACCENT}" stroke-width="2"/>')
            parts.append(f'<path d="M{ax+6} {y+bh/2-5} L{ax+14} {y+bh/2} '
                         f'L{ax+6} {y+bh/2+5}" fill="{ACCENT}"/>')
    parts.append("</svg>")
    return "".join(parts)


def svg_compare(title: str, left: dict, right: dict) -> str:
    w, pad = 720, 40
    rows = max(len(left["items"]), len(right["items"]))
    h = 130 + rows * 36
    colw = (w - pad * 3) / 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
        f'<text x="{w/2}" y="40" font-size="22" font-weight="700" '
        f'text-anchor="middle" fill="{INK}" font-family="{FONT}">{_esc(title)}</text>',
    ]
    for idx, (col, x0) in enumerate([(left, pad), (right, pad * 2 + colw)]):
        parts.append(f'<rect x="{x0}" y="64" width="{colw}" height="{h-90}" '
                     f'rx="10" fill="{BOX}" stroke="{LINE}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x0+colw/2}" y="92" font-size="17" '
                     f'font-weight="700" text-anchor="middle" fill="{ACCENT}" '
                     f'font-family="{FONT}">{_esc(col["header"])}</text>')
        yy = 122
        for it in col["items"]:
            parts.append(f'<text x="{x0+20}" y="{yy}" font-size="15" '
                         f'fill="{INK}" font-family="{FONT}">• {_esc(it)}</text>')
            yy += 32
    parts.append("</svg>")
    return "".join(parts)


def svg_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    w, pad = 720, 40
    ncol = len(headers)
    colw = (w - pad * 2) / ncol
    rh = 40
    h = 100 + (len(rows) + 1) * rh
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
        f'<text x="{w/2}" y="44" font-size="22" font-weight="700" '
        f'text-anchor="middle" fill="{INK}" font-family="{FONT}">{_esc(title)}</text>',
    ]
    y0 = 70
    # header row
    parts.append(f'<rect x="{pad}" y="{y0}" width="{w-2*pad}" height="{rh}" '
                 f'fill="{ACCENT}"/>')
    for c, hd in enumerate(headers):
        parts.append(f'<text x="{pad+c*colw+12}" y="{y0+26}" font-size="15" '
                     f'font-weight="700" fill="#ffffff" '
                     f'font-family="{FONT}">{_esc(hd)}</text>')
    for r, row in enumerate(rows):
        ry = y0 + (r + 1) * rh
        fill = BOX if r % 2 == 0 else "#eef2f7"
        parts.append(f'<rect x="{pad}" y="{ry}" width="{w-2*pad}" height="{rh}" '
                     f'fill="{fill}" stroke="{LINE}" stroke-width="0.5"/>')
        for c, cell in enumerate(row):
            parts.append(f'<text x="{pad+c*colw+12}" y="{ry+26}" font-size="14" '
                         f'fill="{INK}" font-family="{FONT}">{_esc(cell)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_svg(diagram: dict) -> str:
    kind = diagram.get("kind")
    title = diagram.get("title", "")
    if kind == "flow":
        return svg_flow(title, diagram["steps"])
    if kind == "compare":
        return svg_compare(title, diagram["left"], diagram["right"])
    if kind == "table":
        return svg_table(title, diagram["headers"], diagram["rows"])
    raise ValueError(f"unknown diagram kind: {kind}")


def render_png(svg: str, out_png: Path, chrome: str) -> bool:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    svg_file = out_png.with_suffix(".svg")
    svg_file.write_text(svg, encoding="utf-8")
    # derive size from the svg header
    import re
    m = re.search(r'width="(\d+)" height="(\d+)"', svg)
    size = f"{m.group(1)},{m.group(2)}" if m else "720,480"
    out_abs = out_png.resolve()
    svg_abs = svg_file.resolve()
    cmd = [chrome, "--headless", "--disable-gpu", "--force-device-scale-factor=2",
           f"--screenshot={out_abs}", f"--window-size={size}",
           "--default-background-color=ffffffff",
           svg_abs.as_uri()]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return out_png.exists() and out_png.stat().st_size > 0


def run(plan_path: str, out_dir: str, report_path: str) -> dict[str, Any]:
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    assets = plan.get("assets", {})
    out_dir = Path(out_dir)
    chrome = find_chrome()
    results: list[dict] = []
    for name, spec in assets.items():
        rec: dict[str, Any] = {"name": name, "type": spec.get("type")}
        if spec.get("type") == "figure" and "diagram" in spec:
            if not chrome:
                rec.update(status="deferred",
                           reason="no chrome/svg renderer available")
                results.append(rec)
                continue
            # honor the plan's relative output path (e.g. assets/figure-x.png)
            rel = spec.get("output", f"assets/{name}.png")
            out_png = out_dir / rel
            try:
                svg = build_svg(spec["diagram"])
                ok = render_png(svg, out_png, chrome)
                rec.update(status="ok" if ok else "failed",
                           output=str(out_png) if ok else None,
                           used_real_renderer=True, renderer="chrome-headless")
            except Exception as exc:  # noqa: BLE001
                rec.update(status="failed", reason=str(exc))
        else:
            # creative image: no text-to-image backend -> deferred, keep prompt
            rec.update(status="deferred",
                       reason="needs text-to-image model (no backend configured)",
                       prompt=spec.get("prompt"),
                       output=spec.get("output"))
        results.append(rec)
    payload = {
        "chrome": chrome,
        "generated": [r for r in results if r.get("status") == "ok"],
        "deferred": [r for r in results if r.get("status") == "deferred"],
        "failed": [r for r in results if r.get("status") == "failed"],
        "assets": results,
    }
    Path(report_path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--report", required=True)
    a = ap.parse_args()
    r = run(a.plan, a.out_dir, a.report)
    print(json.dumps({k: len(v) for k, v in r.items()
                      if k in ("generated", "deferred", "failed")},
                     ensure_ascii=False))

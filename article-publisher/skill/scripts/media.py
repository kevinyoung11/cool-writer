"""Media planning for the article-publisher skill.

Articles for 公众号/知乎 are image-heavy formats. The source script carries
"画面建议"/流程图/对比图/分工表 that must become either (a) real figures with
generation prompts, or (b) retained structure diagrams (code block / table /
mermaid) in the prose.

This module is deterministic: it does NOT generate images. It (1) derives how
many figures the draft *should* have from the v1 sizing rule, (2) validates a
media plan the LLM authored, and (3) reports figure coverage so the checklist
can flag an under-illustrated article.

v1 sizing rule (design/v1/talk-v1.md):
  - 总览图: 1
  - 每 1200-1800 字: 1 张解释图
  - 方法论文章: 至少 3 张
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
# A retained "structure diagram" counts as visual support too: fenced code
# blocks used as flow/compare diagrams, markdown tables, or mermaid.
FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
TABLE_RE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)


@dataclass
class MediaReport:
    chars: int = 0
    recommended_min: int = 0
    images: int = 0
    structure_diagrams: int = 0
    planned: int = 0
    missing_prompts: list[str] = field(default_factory=list)

    @property
    def visual_total(self) -> int:
        return self.images + self.structure_diagrams

    @property
    def passed(self) -> bool:
        return self.visual_total >= self.recommended_min

    def to_dict(self) -> dict[str, Any]:
        return {
            "chars": self.chars,
            "recommended_min_figures": self.recommended_min,
            "inline_images": self.images,
            "structure_diagrams": self.structure_diagrams,
            "visual_total": self.visual_total,
            "planned_in_media_plan": self.planned,
            "missing_prompts": self.missing_prompts,
            "passed": self.passed,
        }


def recommend_count(chars: int, is_methodology: bool = True) -> int:
    by_length = max(1, round(chars / 1500))   # 1 总览 + 每 ~1500 字一张
    floor = 3 if is_methodology else 1
    return max(floor, by_length)


def count_visuals(md: str) -> tuple[int, int]:
    images = len(IMG_RE.findall(md))
    diagrams = 0
    for lang, body in FENCE_RE.findall(md):
        # treat non-code fences (text/diagram) and mermaid as structure diagrams
        if lang.strip().lower() in ("", "text", "mermaid", "diagram") and body.strip():
            diagrams += 1
    # tables: count contiguous table blocks, not rows
    rows = TABLE_RE.findall(md)
    if rows:
        diagrams += 1
    return images, diagrams


def analyze(draft_md: str, media_plan: dict | None,
            is_methodology: bool = True) -> MediaReport:
    rep = MediaReport()
    rep.chars = len(draft_md)
    rep.recommended_min = recommend_count(rep.chars, is_methodology)
    rep.images, rep.structure_diagrams = count_visuals(draft_md)
    if media_plan:
        assets = media_plan.get("assets", media_plan)
        if isinstance(assets, dict):
            rep.planned = len(assets)
            for name, spec in assets.items():
                if isinstance(spec, dict):
                    # figure-type assets are rendered from a `diagram` spec and
                    # need no text prompt; only creative images need a prompt.
                    if spec.get("type") == "figure" or "diagram" in spec:
                        continue
                    prompt = spec.get("prompt")
                else:
                    prompt = spec
                if not prompt:
                    rep.missing_prompts.append(name)
    return rep


def run(draft_path: str, plan_path: str | None, out_path: str,
        is_methodology: bool = True) -> dict[str, Any]:
    md = Path(draft_path).read_text(encoding="utf-8")
    plan = None
    if plan_path and Path(plan_path).exists():
        try:
            plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            plan = None
    rep = analyze(md, plan, is_methodology)
    payload = {"draft": draft_path, "plan": plan_path, "result": rep.to_dict()}
    Path(out_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--plan")
    ap.add_argument("--out", required=True)
    ap.add_argument("--non-methodology", action="store_true")
    a = ap.parse_args()
    r = run(a.draft, a.plan, a.out, is_methodology=not a.non_methodology)
    print(json.dumps(r["result"], ensure_ascii=False, indent=2))

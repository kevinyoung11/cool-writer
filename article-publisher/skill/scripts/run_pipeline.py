#!/usr/bin/env python3
"""article-publisher deterministic pipeline.

Scope: take an *existing* script/article and turn it into publishable WeChat
公众号 and 知乎 versions. The deep, taste-driven rewriting is done by the LLM
(see SKILL.md); this driver owns the *deterministic* half:

  1. canonicalize the source markdown
  2. lint the canonical + each platform draft with real OSS tools
  3. format each platform draft to styled HTML via wenyan (OSS)
  4. fidelity-check each platform draft against protected spans
  5. emit report.json + publish-checklist.md, surfacing any DEGRADED steps

It never fabricates tool success: when a tool can't run, its record says
status=unavailable/failed and fallback_used is set, and the checklist flags it.

Usage:
  run_pipeline.py --source PATH --slug NAME [--stage canonical|lint|format|all]
  run_pipeline.py --source PATH --slug NAME --wechat W.md --zhihu Z.md --stage publish
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import adapters  # noqa: E402
import fidelity  # noqa: E402


def load_config() -> dict:
    cfg = json.loads((HERE.parent / "config" / "defaults.json").read_text("utf-8"))
    return cfg


def canonicalize(source_md: str) -> str:
    """Light, deterministic cleanup. No content rewriting."""
    text = source_md.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)          # trailing ws
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse blank runs
    return text.strip() + "\n"


def health_report(cfg: dict) -> dict:
    toolbox = Path(cfg["toolbox"])
    skill_root = Path(cfg["skill_root"])
    out = {}
    for name, tcfg in cfg["tools"].items():
        ad = adapters.build_adapter(name, toolbox, tcfg, skill_root)
        ok, detail = ad.can_run()
        out[name] = {"available": ok, "bin": ad._bin, "detail": detail}
    return out


def lint_file(cfg: dict, md_path: Path, out_dir: Path) -> list[adapters.ToolResult]:
    toolbox = Path(cfg["toolbox"])
    skill_root = Path(cfg["skill_root"])
    results = []
    for name, tcfg in cfg["tools"].items():
        if tcfg.get("kind") != "lint":
            continue
        ad = adapters.build_adapter(name, toolbox, tcfg, skill_root)
        ok, detail = ad.can_run()
        if not ok:
            results.append(adapters.ToolResult(
                name=name, kind="lint", status="unavailable",
                used_real_tool=False, fallback_used=True,
                detail=f"can_run=false: {detail}"))
            continue
        results.append(ad.run(md_path, out_dir))
    return results


def format_file(cfg: dict, md_path: Path, out_dir: Path, platform: str
                ) -> adapters.ToolResult:
    toolbox = Path(cfg["toolbox"])
    skill_root = Path(cfg["skill_root"])
    tcfg = cfg["tools"]["wenyan"]
    ad = adapters.build_adapter("wenyan", toolbox, tcfg, skill_root)
    ok, detail = ad.can_run()
    if not ok:
        return adapters.ToolResult(
            name="wenyan", kind="format", status="unavailable",
            used_real_tool=False, fallback_used=True,
            detail=f"can_run=false: {detail}")
    theme = cfg["wenyan"][f"{platform}_theme"]
    hl = cfg["wenyan"]["highlight"]
    return ad.run(md_path, out_dir, theme=theme, highlight=hl, label=platform)


def write_checklist(out_dir: Path, slug: str, platforms: list[str],
                    tool_results: dict, fidelity_results: dict,
                    health: dict) -> Path:
    degraded = []
    for scope, results in tool_results.items():
        for r in results:
            if r["status"] in ("unavailable", "failed") or r["fallback_used"]:
                degraded.append(f"- [{scope}] **{r['name']}** → {r['status']}"
                                f" ({r['detail']})")
    lines = [f"# 发布前检查清单 — {slug}", ""]
    lines.append("## 工具健康检查")
    for name, h in health.items():
        mark = "✅" if h["available"] else "❌"
        lines.append(f"- {mark} `{name}` — {h['detail']}")
    lines.append("")
    lines.append("## 降级提示（需人工复核）")
    lines += (degraded or ["- 无：所有步骤均由真实开源工具完成。"])
    lines.append("")
    lines.append("## 保真度（数字/术语/代码/链接）")
    for plat, fr in fidelity_results.items():
        r = fr["result"]
        mark = "✅" if r["passed"] else "❌"
        lines.append(f"- {mark} **{plat}**：{r['preserved']}/"
                     f"{r['total_protected_spans']} 保留，score={r['score']}")
        for m in r["missing"][:10]:
            lines.append(f"    - 缺失[{m['category']}]：`{m['span']}`")
    lines.append("")
    lines.append("## 平台合规（人工确认）")
    if "wechat" in platforms:
        lines += [
            "### 微信公众号",
            "- [ ] 标题 / 封面裁剪 / 摘要已设置",
            "- [ ] 原创/转载声明正确",
            "- [ ] 外链已按公众号政策处理（正文不可点外链）",
            "- [ ] 粘贴 `wenyan-wechat.html` 内联样式到编辑器后排版正常",
        ]
    if "zhihu" in platforms:
        lines += [
            "### 知乎",
            "- [ ] 首图可作为信息流预览",
            "- [ ] 已移除微信专用话术（如“点击上方关注”）",
            "- [ ] 代码块/公式在知乎渲染正常",
        ]
    p = out_dir / "publish-checklist.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--stage", default="all",
                    choices=["health", "canonical", "lint", "format",
                             "fidelity", "publish", "all"])
    ap.add_argument("--wechat", help="path to LLM-rewritten wechat.md")
    ap.add_argument("--zhihu", help="path to LLM-rewritten zhihu.md")
    ap.add_argument("--terms", help="protected-spans terms json (optional)")
    args = ap.parse_args()

    cfg = load_config()
    out_dir = Path(cfg["output_root"]) / args.slug
    tool_dir = out_dir / "tool-results"
    out_dir.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)

    source = Path(args.source)
    health = health_report(cfg)

    if args.stage == "health":
        print(json.dumps(health, ensure_ascii=False, indent=2))
        return 0

    # canonical
    canonical = canonicalize(source.read_text("utf-8"))
    canon_path = out_dir / "canonical.md"
    canon_path.write_text(canonical, encoding="utf-8")
    (out_dir / "source-original.md").write_text(source.read_text("utf-8"), "utf-8")

    report = {
        "slug": args.slug,
        "source": str(source),
        "platforms": cfg["platforms"],
        "health": health,
        "tools": {},
        "fidelity": {},
    }

    tool_results: dict[str, list[dict]] = {}
    fidelity_results: dict[str, dict] = {}

    # lint canonical always
    canon_lint = lint_file(cfg, canon_path, tool_dir)
    tool_results["canonical"] = [asdict(r) for r in canon_lint]

    platform_files = {}
    if args.wechat:
        platform_files["wechat"] = Path(args.wechat)
    if args.zhihu:
        platform_files["zhihu"] = Path(args.zhihu)

    for plat, pf in platform_files.items():
        if not pf.exists():
            continue
        dst = out_dir / f"{plat}.md"
        dst.write_text(pf.read_text("utf-8"), encoding="utf-8")
        # lint
        lr = lint_file(cfg, dst, tool_dir)
        # format
        fr_tool = format_file(cfg, dst, tool_dir, plat)
        lr.append(fr_tool)
        if fr_tool.status == "ok" and fr_tool.output_files:
            # promote the styled html next to the platform md
            html_dst = out_dir / f"{plat}.html"
            html_dst.write_text(Path(fr_tool.output_files[0]).read_text("utf-8"),
                                encoding="utf-8")
        tool_results[plat] = [asdict(r) for r in lr]
        # fidelity
        fid = fidelity.run(str(canon_path), str(dst), args.terms,
                           str(out_dir / f"fidelity-{plat}.json"))
        fidelity_results[plat] = fid

    report["tools"] = tool_results
    report["fidelity"] = {k: v["result"] for k, v in fidelity_results.items()}
    (out_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    write_checklist(out_dir, args.slug, cfg["platforms"],
                    tool_results, fidelity_results, health)

    # console summary
    used_real = sum(1 for rs in tool_results.values() for r in rs
                    if r["used_real_tool"] and r["status"] == "ok")
    print(f"[ok] run -> {out_dir}")
    print(f"     real OSS tool successes: {used_real}")
    for plat, fr in fidelity_results.items():
        r = fr["result"]
        print(f"     fidelity[{plat}]: {r['preserved']}/{r['total_protected_spans']}"
              f" passed={r['passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

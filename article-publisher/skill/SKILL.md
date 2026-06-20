---
name: article-publisher
description: Polish an existing Chinese script/article and rewrite it into publishable 微信公众号 and 知乎 versions. Use when the user has a finished draft/script and wants 公众号/知乎 发布版、润色改写、平台化排版, with real lint + wenyan formatting and a fidelity/compliance checklist.
---

# Article Publisher (脚本 → 公众号 / 知乎 可发布版)

This skill takes an **existing** script or article and produces publishable
WeChat 公众号 and 知乎 versions. It does **not** generate articles from scratch
and does **not** do video/storyboard/editing — input is already-written content.

Two cooperating halves:

- **LLM editing chain (you, following the stages below)** — diagnosis, deep
  rewrite, style alignment, 说人话 pass. This is the taste-driven part.
- **Deterministic pipeline (`scripts/run_pipeline.py`)** — canonicalize, lint
  with real OSS tools, format with wenyan, fidelity-check, and emit the report
  + publish checklist. This is the verifiable part.

Keep all artifacts under `/Users/apulu/Documents/yy-article/article-publisher/runs/<slug>/`.

## One-time setup

The OSS tools are installed locally in `tools/` (pinned in `tools/package.json`).
If `runs` show tools `unavailable`, reinstall:

```bash
cd /Users/apulu/Documents/yy-article/article-publisher/skill/tools && npm install
```

Verify health any time:

```bash
python3 /Users/apulu/Documents/yy-article/article-publisher/skill/scripts/run_pipeline.py \
  --source ANY.md --slug _health --stage health
```

All four (`lint-md`, `zhlint`, `textlint`, `wenyan`) should report `available: true`.

## Workflow

### 1. Intake & diagnosis (LLM)
- Read the source. Identify: core thesis, usable material, what's video-only
  (口播重复、制作指令、时间码) that must be cut for an article, and per-platform
  resistance (微信要现场感/短段落/推进感；知乎要结论/定义/论证链/边界).
- Write `analysis/content-diagnosis.md` and per-platform `*-edit-plan.md`.
- List protected facts (numbers, 术语, 项目名) into `analysis/protected-terms.json`:
  `{"terms": [...], "project_names": [...]}`. The fidelity check also auto-extracts
  code/URLs/numbers, so only add terms not literally present as code.

### 2. Deep rewrite (LLM) — one draft per platform
- Rewrite from `canonical.md`, not the raw source.
- **微信公众号**: short paragraphs, strong opening现场感, conversational推进, 关键句可做字幕级金句.
- **知乎**: clear结论先行、定义、论证链、边界、少口语.
- **Style alignment**: pull voice from `kazike-writing-methodology-lite.md`
  (站在第一现场、普通人能懂、工具+趋势+案例+行动). Match cadence, not just topic.
- **Do not** invent new cases/data/credentials. Preserve every number, term,
  code block, link, project name. (The pipeline will verify this.)
- Write `wechat.md` and `zhihu.md` (body only; no video production notes).

### 3. Run the deterministic pipeline
```bash
python3 /Users/apulu/Documents/yy-article/article-publisher/skill/scripts/run_pipeline.py \
  --source <SOURCE.md> --slug <slug> \
  --wechat <wechat.md> --zhihu <zhihu.md> \
  --terms <analysis/protected-terms.json> \
  --stage all
```
This produces, under `runs/<slug>/`: `canonical.md`, `wechat.md`/`zhihu.md`,
`wechat.html`/`zhihu.html` (wenyan inline-styled), `tool-results/`,
`fidelity-*.json`, `report.json`, `publish-checklist.md`.

### 4. Review the report (LLM + human)
- Open `publish-checklist.md`.
- **Fidelity**: any `❌` means a number/term/code/link was dropped or mutated.
  Fix the draft and rerun. A drop may be intentional (e.g. cutting a video-only
  number) — if so, note it; otherwise restore it.
- **Degradation**: if any tool is `unavailable/failed`, the HTML/lint for that
  step is degraded — fix the tool (see setup) or flag for manual formatting.
- **Lint**: skim `tool-results/` for 中英文空格、全角标点、技术写作问题; apply fixes.

### 5. Hand off
- 公众号: paste `wechat.html` into the MP editor (inline styles survive paste).
- 知乎: paste `zhihu.md` (知乎 has its own editor) or `zhihu.html`; confirm首图.
- Walk the compliance checkboxes before publishing. **Publishing itself is a
  human action** — this skill never posts.

## Theme tuning
Edit `config/defaults.json` → `wenyan.wechat_theme` / `zhihu_theme`. Available
themes: `default, lapis, orangeheart, rainbow, pie, maize, purple, phycat`
(list with `tools/node_modules/.bin/wenyan theme --list`).

## What this skill guarantees vs. not
- **Guaranteed (deterministic)**: real OSS tools run or are reported as failed;
  styled HTML is produced by wenyan, not faked; protected facts are diffed.
- **Not guaranteed (needs human judgment)**: taste, platform compliance,
  cover/title, whether a dropped number was intentional.

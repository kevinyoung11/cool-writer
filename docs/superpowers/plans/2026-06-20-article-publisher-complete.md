# Article Publisher Complete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Markdown-to-publish-package pipeline for WeChat Official Account and Zhihu outputs.

**Architecture:** Add a Python pipeline package under the existing `article-publisher` skill. Keep default behavior local and non-destructive, with optional safe external tool discovery. Produce deterministic platform files, reports, and media briefs even when external tools are missing.

**Tech Stack:** Python standard library, pytest-compatible tests via `unittest`, existing Codex skill folder layout.

---

## File Structure

- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/__init__.py`: package marker and public version.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/markdown.py`: metadata parsing, slugging, markdown helpers.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/checks.py`: static article checks.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/renderers.py`: WeChat and Zhihu output generation.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/tools.py`: local tool discovery and safe command definitions.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/media.py`: Image Gen and Remotion brief generation.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/report.py`: checklist and JSON report writing.
- Create `/Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py`: CLI orchestration.
- Modify `/Users/apulu/.codex/skills/article-publisher/scripts/check_article.py`: reuse new checks while preserving existing CLI behavior.
- Create `/Users/apulu/.codex/skills/article-publisher/tests/test_article_pipeline.py`: behavior tests.
- Modify `/Users/apulu/.codex/skills/article-publisher/SKILL.md`: document the full pipeline and safety boundary.
- Create `/Users/apulu/.codex/skills/article-publisher/references/output-contract.md`: output file contract.
- Create `/Users/apulu/.codex/skills/article-publisher/references/media-generation.md`: Image Gen and Remotion workflow.
- Create `/Users/apulu/.codex/skills/article-publisher/references/local-projects.md`: local project adapter notes.

## Task 1: Tests For Core Markdown And Checks

**Files:**
- Create: `/Users/apulu/.codex/skills/article-publisher/tests/test_article_pipeline.py`

- [ ] **Step 1: Write failing tests**

Write tests that import the planned modules and assert:

- front matter, H1 title, summary, cover, and slug are extracted
- missing image and placeholder findings are reported
- code fences remain protected in rendered outputs
- publish package command writes expected files

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
python -m unittest discover -s tests -v
```

Expected: fail with missing `article_pipeline` modules.

## Task 2: Markdown Parsing And Checks

**Files:**
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/__init__.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/markdown.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/checks.py`

- [ ] **Step 1: Implement minimal parsing and checks**

Implement dataclasses for metadata, article model, and finding objects. Support simple YAML-like front matter, H1 extraction, slug generation, image/link extraction, local image/link checks, code fence balance, and placeholder checks.

- [ ] **Step 2: Run tests**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
python -m unittest discover -s tests -v
```

Expected: parsing/check tests pass; renderer/package tests still fail.

## Task 3: Renderers, Media, And Reports

**Files:**
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/renderers.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/media.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/report.py`

- [ ] **Step 1: Implement output generators**

Implement deterministic WeChat Markdown, WeChat HTML, Zhihu Markdown, media plan markdown, image prompts JSON, motion brief, checklist markdown, and report JSON writers.

- [ ] **Step 2: Run tests**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
python -m unittest discover -s tests -v
```

Expected: renderer/media/report tests pass; CLI tests still fail.

## Task 4: CLI Orchestration And Tool Discovery

**Files:**
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/tools.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py`
- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/check_article.py`

- [ ] **Step 1: Implement CLI and compatibility wrapper**

Implement `article_publish.py` with input validation, platform flags, output directory, slug override, cover/summary/title override, media and motion flags, safe tool discovery, and package writing.

Update `check_article.py` so existing usage still prints/writes checklist output using the new check engine.

- [ ] **Step 2: Run tests**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
python -m unittest discover -s tests -v
```

Expected: all unit tests pass.

## Task 5: Skill Instructions And References

**Files:**
- Modify: `/Users/apulu/.codex/skills/article-publisher/SKILL.md`
- Modify: `/Users/apulu/.codex/skills/article-publisher/agents/openai.yaml`
- Create: `/Users/apulu/.codex/skills/article-publisher/references/output-contract.md`
- Create: `/Users/apulu/.codex/skills/article-publisher/references/media-generation.md`
- Create: `/Users/apulu/.codex/skills/article-publisher/references/local-projects.md`

- [ ] **Step 1: Document the workflow**

Update the skill to instruct future Codex runs to prefer `article_publish.py`, use external tools only when safe and available, and use Image Gen/Remotion only from generated briefs and explicit user intent.

- [ ] **Step 2: Validate skill**

Run:

```bash
python /Users/apulu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/apulu/.codex/skills/article-publisher
```

Expected: validation passes.

## Task 6: End-To-End Verification

**Files:**
- No new files required beyond generated test output under a temporary directory.

- [ ] **Step 1: Run unit tests**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run pipeline on a real local Markdown file**

Run:

```bash
python /Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py \
  /Users/apulu/Documents/yy-article/kazike-writing-methodology-lite.md \
  --platform wechat \
  --platform zhihu \
  --out-dir /tmp/article-publisher-e2e \
  --media-plan \
  --motion-plan
```

Expected: output package exists with `wechat.md`, `wechat.html`, `zhihu.md`, `publish-checklist.md`, `report.json`, `media/media-plan.md`, `media/image-prompts.json`, `media/motion-brief.md`, and logs.

- [ ] **Step 3: Inspect key outputs**

Run:

```bash
find /tmp/article-publisher-e2e -maxdepth 3 -type f | sort
python -m json.tool /tmp/article-publisher-e2e/kazike-writing-methodology-lite/report.json >/tmp/article-publisher-report.pretty.json
```

Expected: files are present and report JSON is valid.

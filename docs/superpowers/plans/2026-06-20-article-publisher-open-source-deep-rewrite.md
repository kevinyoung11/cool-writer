# Article Publisher Open Source Deep Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `article-publisher` into a local article editing and publishing workbench that deeply rewrites video scripts into platform-native WeChat/Zhihu articles and truly invokes the approved local open source projects.

**Architecture:** Build this as two cooperating chains. The content chain creates diagnosis, platform edit plans, deep drafts, and reviews. The tool chain invokes local open source adapters, records real execution results, and feeds checked outputs into the final package. Existing Python fallback behavior remains, but reports must clearly distinguish fallback from successful real open source integrations.

**Tech Stack:** Python 3 standard library, `unittest`, local Node/npm/pnpm projects under `/Users/apulu/Documents/yy-article/docs/projects`, Codex/Image Gen for deep editorial and generated images, optional Remotion brief outputs only unless explicitly rendered.

---

## Long-Term Roadmap

### Phase 1: Real Toolchain + Traceable Package

Deliver a deterministic pipeline that:

- creates full package directories: `analysis/`, `drafts/`, `tool-results/`, `reviews/`, `media/`, `assets/`, `logs/`
- runs adapter discovery for every approved local project
- invokes safe real project entry points where possible
- blocks upload/login/draft/publish/sync commands
- upgrades `report.json` and `publish-checklist.md`
- keeps existing platform outputs working

### Phase 2: Deep Editorial Workbench

Deliver a content chain that:

- generates content diagnosis
- creates WeChat and Zhihu edit plans
- creates deep platform drafts
- preserves protected spans
- reviews text quality before final render
- makes article quality materially better than script cleanup

### Phase 3: Structure-Driven Media

Deliver media planning that:

- creates 3-5 media slots for long methodology articles
- generates Image Gen prompts per slot
- supports replacing placeholders with generated/reused local assets
- produces Remotion `brief_only` outputs unless explicit render is requested

### Phase 4: Full End-to-End Acceptance

Run the upgraded pipeline on:

`/Users/apulu/Documents/yy-article/write-v2/vibe-ai-problem-solving-video-script.md`

Acceptance requires:

- final WeChat/Zhihu outputs are publishable
- all package reports are self-consistent
- real open source project integrations are recorded
- required images are resolved
- tests pass
- skill validation passes
- subagent review passes

---

## File Structure

Create:

- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/__init__.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/base.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/lint_md.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/textlint.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/zhlint.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/md2wechat.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/wenyan.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/markdown_nice.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/runner.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/__init__.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/diagnosis.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/planning.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/deep_rewrite.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/review.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/schemas.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/source_structure.py`
- `/Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py`
- `/Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py`
- `/Users/apulu/.codex/skills/article-publisher/tests/test_media_slots.py`
- `/Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py`

Modify:

- `/Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/assets.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/checks.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/markdown.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/media.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/renderers.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/report.py`
- `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/tools.py`
- `/Users/apulu/.codex/skills/article-publisher/tests/test_article_pipeline.py`
- `/Users/apulu/.codex/skills/article-publisher/SKILL.md`
- `/Users/apulu/.codex/skills/article-publisher/references/output-contract.md`
- `/Users/apulu/.codex/skills/article-publisher/references/local-projects.md`
- `/Users/apulu/.codex/skills/article-publisher/references/platform-tools.md`

---

## Task 1: Adapter Base Contract

**Files:**

- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/__init__.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/base.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py`

- [ ] **Step 1: Write failing adapter result tests**

Add to `test_adapters.py`:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from article_pipeline.adapters.base import AdapterResult, CommandSpec, block_unsafe_command, tail_text, write_adapter_result


class AdapterBaseTests(unittest.TestCase):
    def test_adapter_result_serializes_real_project_metadata(self) -> None:
        result = AdapterResult(
            name="lint-md",
            project_path="/tmp/lint-md",
            command=["node", "runner.js"],
            status="completed",
            used_real_project=True,
            output_files=["tool-results/lint-md.json"],
            stdout_tail="ok",
            stderr_tail="",
            fallback_used=False,
        )

        data = result.to_dict()

        self.assertEqual(data["name"], "lint-md")
        self.assertEqual(data["project_path"], "/tmp/lint-md")
        self.assertEqual(data["command"], ["node", "runner.js"])
        self.assertEqual(data["status"], "completed")
        self.assertTrue(data["used_real_project"])
        self.assertFalse(data["fallback_used"])

    def test_write_adapter_result_creates_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tool-results" / "adapter.json"
            result = AdapterResult(name="x", project_path=None, command=[], status="unavailable")

            write_adapter_result(path, result)

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "unavailable")

    def test_tail_text_limits_long_output(self) -> None:
        text = "a" * 5000
        self.assertEqual(len(tail_text(text, 120)), 120)
        self.assertEqual(tail_text("short", 120), "short")

    def test_block_unsafe_command_blocks_remote_mutation_terms(self) -> None:
        unsafe = CommandSpec(name="md2wechat", args=["md2wechat", "convert", "--draft"])
        safe = CommandSpec(name="md2wechat", args=["md2wechat", "inspect", "article.md"])

        self.assertTrue(block_unsafe_command(unsafe))
        self.assertFalse(block_unsafe_command(safe))
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py -v
```

Expected: import failure because `article_pipeline.adapters.base` does not exist.

- [ ] **Step 3: Implement adapter base**

Create `adapters/__init__.py`:

```python
"""Open source project adapters for article-publisher."""
```

Create `adapters/base.py`:

```python
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


ADAPTER_STATUSES = {"completed", "unavailable", "failed", "skipped", "blocked_unsafe"}
UNSAFE_TERMS = {"upload", "draft", "publish", "login", "sync", "--draft", "--publish", "--upload"}


@dataclass(frozen=True)
class CommandSpec:
    name: str
    args: list[str]
    cwd: str | None = None
    timeout: int = 60


@dataclass(frozen=True)
class AdapterResult:
    name: str
    project_path: str | None
    command: list[str] = field(default_factory=list)
    status: str = "skipped"
    used_real_project: bool = False
    output_files: list[str] = field(default_factory=list)
    stdout_tail: str = ""
    stderr_tail: str = ""
    fallback_used: bool = False
    detail: str = ""

    def to_dict(self) -> dict[str, object]:
        if self.status not in ADAPTER_STATUSES:
            raise ValueError(f"Invalid adapter status: {self.status}")
        return {
            "name": self.name,
            "project_path": self.project_path,
            "command": self.command,
            "status": self.status,
            "used_real_project": self.used_real_project,
            "output_files": self.output_files,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
            "fallback_used": self.fallback_used,
            "detail": self.detail,
        }


def tail_text(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def write_adapter_result(path: Path, result: AdapterResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def block_unsafe_command(command: CommandSpec) -> bool:
    lowered = {part.lower() for part in command.args}
    return bool(lowered & UNSAFE_TERMS)


def run_command(command: CommandSpec) -> AdapterResult:
    if block_unsafe_command(command):
        return AdapterResult(
            name=command.name,
            project_path=command.cwd,
            command=command.args,
            status="blocked_unsafe",
            detail="Command contains upload/login/draft/publish/sync terms.",
        )
    try:
        completed = subprocess.run(
            command.args,
            cwd=command.cwd,
            text=True,
            capture_output=True,
            timeout=command.timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return AdapterResult(
            name=command.name,
            project_path=command.cwd,
            command=command.args,
            status="failed",
            stderr_tail=str(exc),
        )
    return AdapterResult(
        name=command.name,
        project_path=command.cwd,
        command=command.args,
        status="completed" if completed.returncode == 0 else "failed",
        used_real_project=command.cwd is not None,
        stdout_tail=tail_text(completed.stdout),
        stderr_tail=tail_text(completed.stderr),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py -v
```

Expected: PASS.

---

## Task 2: Source Structure and Protected Spans

**Files:**

- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/source_structure.py`
- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/markdown.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py`

- [ ] **Step 1: Write failing source structure tests**

Add to `test_editorial_pipeline.py`:

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from article_pipeline.markdown import parse_article
from article_pipeline.source_structure import build_source_structure, extract_protected_spans


class SourceStructureTests(unittest.TestCase):
    def test_build_source_structure_records_headings_and_script_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "script.md"
            path.write_text(
                "# 标题\n\n**画面建议：**\n\n不要发布。\n\n**口播：**\n\n保留正文。\n\n## 1. 方法\n\n正文。\n",
                encoding="utf-8",
            )
            article = parse_article(path)

            structure = build_source_structure(article)

        self.assertEqual(structure["title"], "标题")
        self.assertIn("方法", [heading["text"] for heading in structure["headings"]])
        self.assertIn("画面建议", structure["script_labels"])
        self.assertIn("口播", structure["script_labels"])

    def test_extract_protected_spans_records_code_links_images_and_inline_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "article.md"
            path.write_text(
                "# 标题\n\n![图](a.png)\n\n[链接](https://example.com)\n\n这里有 `inline_code()`。\n\n```bash\nnpm run build\n```\n",
                encoding="utf-8",
            )
            article = parse_article(path)

            spans = extract_protected_spans(article)
            kinds = {span["kind"] for span in spans}

        self.assertIn("image", kinds)
        self.assertIn("link", kinds)
        self.assertIn("inline_code", kinds)
        self.assertIn("code_fence", kinds)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: import failure for `source_structure`.

- [ ] **Step 3: Implement source structure helpers**

Create `source_structure.py`:

```python
from __future__ import annotations

import re

from .markdown import Article, HEADING_RE


SCRIPT_LABEL_RE = re.compile(r"^\*\*(.+?)：\*\*\s*$", re.M)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.M)


def build_source_structure(article: Article) -> dict[str, object]:
    headings = [
        {"level": len(match.group(1)), "text": match.group(2).strip(), "line": article.body.count("\n", 0, match.start()) + 1}
        for match in HEADING_RE.finditer(article.body)
    ]
    labels = sorted({match.group(1).strip() for match in SCRIPT_LABEL_RE.finditer(article.body)})
    return {
        "source": str(article.path),
        "title": article.title,
        "summary": article.metadata.summary,
        "cover": article.metadata.cover,
        "headings": headings,
        "script_labels": labels,
        "image_count": len(article.images),
        "link_count": len(article.links),
    }


def extract_protected_spans(article: Article) -> list[dict[str, object]]:
    spans: list[dict[str, object]] = []
    for image in article.images:
        spans.append({"kind": "image", "value": image.uri, "line": image.line})
    for link in article.links:
        spans.append({"kind": "link", "value": link.uri, "line": link.line})
    for match in INLINE_CODE_RE.finditer(article.body):
        spans.append({"kind": "inline_code", "value": match.group(1), "line": article.body.count("\n", 0, match.start()) + 1})
    for match in CODE_FENCE_RE.finditer(article.body):
        spans.append({"kind": "code_fence", "value": match.group(0), "line": article.body.count("\n", 0, match.start()) + 1})
    return spans
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: PASS.

---

## Task 3: Editorial Diagnosis and Plans

**Files:**

- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/__init__.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/diagnosis.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/planning.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/schemas.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py`

- [ ] **Step 1: Write failing editorial artifact tests**

Append:

```python
from article_pipeline.editorial.diagnosis import build_content_diagnosis
from article_pipeline.editorial.planning import build_platform_edit_plan


class EditorialArtifactTests(unittest.TestCase):
    def test_content_diagnosis_names_thesis_and_quality_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "script.md"
            path.write_text("# 标题\n\n> 核心定位：解释 AI 工作流。\n\n**口播：**\n\n这期视频讲 AI 工作流。\n", encoding="utf-8")
            article = parse_article(path)

            diagnosis = build_content_diagnosis(article)

        self.assertIn("核心主张", diagnosis)
        self.assertIn("质量缺口", diagnosis)
        self.assertIn("平台阻力", diagnosis)

    def test_platform_edit_plan_is_platform_specific(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "script.md"
            path.write_text("# 标题\n\n正文。\n", encoding="utf-8")
            article = parse_article(path)

            wechat = build_platform_edit_plan(article, "wechat")
            zhihu = build_platform_edit_plan(article, "zhihu")

        self.assertIn("现场感", wechat)
        self.assertIn("短段落", wechat)
        self.assertIn("先说结论", zhihu)
        self.assertIn("边界", zhihu)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: import failure for editorial modules.

- [ ] **Step 3: Implement editorial diagnosis/planning**

Create `editorial/__init__.py`:

```python
"""Editorial planning helpers for deep article rewrites."""
```

Create `editorial/schemas.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EditorialArtifacts:
    diagnosis: str
    wechat_plan: str
    zhihu_plan: str
```

Create `editorial/diagnosis.py`:

```python
from __future__ import annotations

from ..markdown import Article
from ..renderers import strip_operational_blocks


def build_content_diagnosis(article: Article) -> str:
    title = article.title or article.path.stem
    summary = article.metadata.summary or "未提取到摘要，需要从正文第一屏重新提炼。"
    cleaned = strip_operational_blocks(article.body)
    body_chars = len(cleaned)
    return f"""# Content Diagnosis

## 核心主张

文章《{title}》的当前核心主张：{summary}

## 可用材料

- 清理后正文长度：{body_chars} 字符
- 可用图片数量：{len(article.images)}
- 可用链接数量：{len(article.links)}

## 质量缺口

- 需要把视频脚本语境改成独立文章语境。
- 需要补足抽象概念背后的解释、例子或边界。
- 需要减少口播重复和制作指令。
- 需要为复杂流程规划配图或动图。

## 平台阻力

- 微信读者需要更强现场感、短段落和推进节奏。
- 知乎读者需要更明确结论、定义、论证链和边界。

## 改写约束

- 不虚构新案例、新数据、新身份背书。
- 保留代码块、命令、链接、数字、项目名和专业术语。
"""
```

Create `editorial/planning.py`:

```python
from __future__ import annotations

from ..markdown import Article


def build_platform_edit_plan(article: Article, platform: str) -> str:
    title = article.title or article.path.stem
    if platform == "wechat":
        return f"""# WeChat Edit Plan

## 文章

{title}

## 改写策略

- 用现场感开头，先说明为什么这件事值得读。
- 保持短段落，每段只推进一个意思。
- 把抽象方法拆成读者能跟上的故事流。
- 在关键概念后补一句解释或类比。
- 结尾落到普通人下一步可以做什么。

## 段落级动作

- 删除画面建议、屏幕字幕、拍摄备注等制作指令。
- 保留口播中的核心判断，但改为文章口吻。
- 把方法论段落改成“现象 -> 问题 -> 机制 -> 行动”。
- 每 1200-1800 字安排一个视觉点。
"""
    if platform == "zhihu":
        return f"""# Zhihu Edit Plan

## 文章

{title}

## 改写策略

- 第一屏先说结论。
- 给核心概念下清楚定义。
- 用分点结构补足论证链。
- 增加边界条件和常见误区。
- 结尾给出可执行步骤，方便收藏。

## 段落级动作

- 删除视频制作指令。
- 把口播表达改为更稳定的论述表达。
- 把核心方法整理成步骤、原则或判断标准。
- 为复杂流程安排图示，辅助理解。
"""
    raise ValueError(f"Unsupported platform: {platform}")
```

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: PASS.

---

## Task 4: Deep Rewrite and Review Artifacts

**Files:**

- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/deep_rewrite.py`
- Create: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/editorial/review.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py`

- [ ] **Step 1: Write failing deep rewrite tests**

Append:

```python
from article_pipeline.editorial.deep_rewrite import build_deep_rewrite
from article_pipeline.editorial.review import review_platform_draft


class DeepRewriteTests(unittest.TestCase):
    def test_deep_rewrite_removes_script_labels_and_preserves_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "script.md"
            path.write_text(
                "# 标题\n\n**画面建议：**\n\n删掉。\n\n**口播：**\n\n这期视频讲 `run()`。\n\n```bash\nnpm test\n```\n",
                encoding="utf-8",
            )
            article = parse_article(path)

            draft = build_deep_rewrite(article, "wechat", "计划")

        self.assertNotIn("画面建议", draft)
        self.assertNotIn("口播", draft)
        self.assertIn("这篇文章讲 `run()`。", draft)
        self.assertIn("```bash\nnpm test\n```", draft)

    def test_review_platform_draft_detects_script_residue(self) -> None:
        review = review_platform_draft("wechat", "# 标题\n\n**画面建议：**\n\n删掉。\n")

        self.assertFalse(review.passed)
        self.assertIn("script-residue", review.findings)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: import failure for deep rewrite modules.

- [ ] **Step 3: Implement deterministic first-pass deep rewrite helpers**

Create `editorial/deep_rewrite.py`:

```python
from __future__ import annotations

from ..markdown import Article
from ..renderers import strip_operational_blocks


def build_deep_rewrite(article: Article, platform: str, edit_plan: str) -> str:
    title = article.title or article.path.stem
    body = strip_operational_blocks(article.body)
    if article.title and body.startswith(f"# {article.title}"):
        body = body.split("\n", 1)[1].lstrip()
    body = body.replace("这期视频", "这篇文章").replace("整期视频", "这篇文章")
    if platform == "wechat":
        lead = "最近我反复看到一个问题：真正难的不是让 AI 生成内容，而是把它组织进一套能验证、能复盘的工作流。"
    elif platform == "zhihu":
        lead = "先说结论：AI 真正改变的不是某一个工具，而是复杂问题被拆解、执行和验收的方式。"
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    return "\n\n".join([f"# {title}", lead, body]).rstrip() + "\n"
```

Create `editorial/review.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


SCRIPT_RESIDUE = ("画面建议", "屏幕字幕", "拍摄备注", "成片验收", "**口播", "视频脚本版本")


@dataclass(frozen=True)
class DraftReview:
    platform: str
    passed: bool
    findings: list[str]

    def to_markdown(self) -> str:
        status = "passed" if self.passed else "failed"
        lines = [f"# {self.platform} Draft Review", "", f"Status: `{status}`", ""]
        if self.findings:
            lines.extend(f"- {finding}" for finding in self.findings)
        else:
            lines.append("- no blocking findings")
        return "\n".join(lines).rstrip() + "\n"


def review_platform_draft(platform: str, markdown: str) -> DraftReview:
    findings: list[str] = []
    if any(token in markdown for token in SCRIPT_RESIDUE):
        findings.append("script-residue")
    if len(markdown.strip()) < 200:
        findings.append("too-short")
    return DraftReview(platform=platform, passed=not findings, findings=findings)
```

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_editorial_pipeline.py -v
```

Expected: PASS.

---

## Task 5: Media Slot Planning

**Files:**

- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/media.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_media_slots.py`

- [ ] **Step 1: Write failing media slot tests**

Create `test_media_slots.py`:

```python
from __future__ import annotations

import unittest

from article_pipeline.media import build_media_slots


class MediaSlotTests(unittest.TestCase):
    def test_methodology_article_gets_multiple_required_slots(self) -> None:
        markdown = "# 标题\n\n" + "\n\n".join(["AI 方法论正文。"] * 260)

        slots = build_media_slots(markdown, ["wechat", "zhihu"])
        ids = [slot["id"] for slot in slots]

        self.assertIn("figure-01-overview", ids)
        self.assertIn("figure-02-flow", ids)
        self.assertIn("figure-03-comparison", ids)
        self.assertGreaterEqual(len([slot for slot in slots if slot["type"] == "image"]), 3)

    def test_short_article_gets_one_inline_slot(self) -> None:
        slots = build_media_slots("# 标题\n\n短文。", ["wechat"])

        image_slots = [slot for slot in slots if slot["type"] == "image"]
        self.assertEqual(len(image_slots), 1)
        self.assertEqual(image_slots[0]["id"], "figure-01-overview")
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_media_slots.py -v
```

Expected: import failure for `build_media_slots`.

- [ ] **Step 3: Implement media slot planner**

Add to `media.py`:

```python
def build_media_slots(markdown: str, platforms: list[str]) -> list[dict[str, object]]:
    text_length = len(markdown)
    is_methodology = any(token in markdown for token in ("方法论", "流程", "闭环", "步骤", "AI"))
    image_count = 1
    if text_length >= 1000:
        image_count = 2
    if text_length >= 3000:
        image_count = 3
    if text_length >= 6000:
        image_count = max(4, text_length // 1600)
    if is_methodology:
        image_count = max(image_count, 3)
    templates = [
        ("figure-01-overview", "image", "解释全文核心观点总览"),
        ("figure-02-flow", "image", "解释关键流程或步骤"),
        ("figure-03-comparison", "image", "解释错误做法和正确做法的对照"),
        ("figure-04-verification", "image", "解释验证、反驳或复盘闭环"),
        ("figure-05-action", "image", "解释读者行动清单"),
    ]
    slots = [
        {
            "id": slot_id,
            "platforms": platforms,
            "type": slot_type,
            "insert_after_heading": "auto",
            "purpose": purpose,
            "source_excerpt": "",
            "required": True,
            "executor": "imagegen",
            "status": "planned",
        }
        for slot_id, slot_type, purpose in templates[:image_count]
    ]
    if is_methodology:
        slots.append(
            {
                "id": "motion-01-loop",
                "platforms": platforms,
                "type": "motion",
                "insert_after_heading": "auto",
                "purpose": "用 6-8 秒动图解释文章核心闭环",
                "source_excerpt": "",
                "required": False,
                "executor": "remotion",
                "status": "brief_only",
            }
        )
    return slots
```

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_media_slots.py -v
```

Expected: PASS.

---

## Task 6: Open Source Adapter Implementations

**Files:**

- Create: adapter files under `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/adapters/`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py`

- [ ] **Step 1: Write failing project discovery tests**

Append:

```python
from article_pipeline.adapters.lint_md import LINT_MD_PROJECT, run_lint_md
from article_pipeline.adapters.md2wechat import MD2WECHAT_PROJECT, run_md2wechat
from article_pipeline.adapters.markdown_nice import MARKDOWN_NICE_PROJECT, run_markdown_nice
from article_pipeline.adapters.textlint import TEXTLINT_PROJECT, run_textlint
from article_pipeline.adapters.wenyan import WENYAN_PROJECT, run_wenyan
from article_pipeline.adapters.zhlint import ZHLINT_PROJECT, run_zhlint


class OpenSourceAdapterTests(unittest.TestCase):
    def test_adapter_project_paths_point_to_local_projects(self) -> None:
        for project in [LINT_MD_PROJECT, MD2WECHAT_PROJECT, MARKDOWN_NICE_PROJECT, TEXTLINT_PROJECT, WENYAN_PROJECT, ZHLINT_PROJECT]:
            self.assertTrue(str(project).startswith("/Users/apulu/Documents/yy-article/docs/projects"))

    def test_md2wechat_blocks_unsafe_draft_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_md2wechat(Path(tmp) / "in.md", Path(tmp), extra_args=["--draft"])

        self.assertEqual(result.status, "blocked_unsafe")

    def test_adapters_return_structured_results_when_input_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.md"
            output = Path(tmp) / "out"
            results = [
                run_lint_md(missing, output),
                run_textlint(missing, output, "wechat"),
                run_zhlint(missing, output, "wechat"),
                run_wenyan(missing, output),
                run_markdown_nice(missing, output, "wechat"),
            ]

        for result in results:
            self.assertIn(result.status, {"failed", "unavailable"})
            self.assertIsInstance(result.to_dict(), dict)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py -v
```

Expected: import failures for adapter modules.

- [ ] **Step 3: Implement minimal real adapter modules**

Each adapter must:

- define project path constants
- check input file existence
- check project path existence
- run a safe project-specific command if available
- return `AdapterResult`

For `md2wechat.py`, implement this exact unsafe guard:

```python
from __future__ import annotations

from pathlib import Path

from .base import AdapterResult, CommandSpec, block_unsafe_command, run_command


MD2WECHAT_PROJECT = Path("/Users/apulu/Documents/yy-article/docs/projects/md2wechat-skill")


def run_md2wechat(input_file: Path, output_dir: Path, extra_args: list[str] | None = None) -> AdapterResult:
    args_tail = extra_args or []
    command = CommandSpec("md2wechat", ["node", "scripts/run.js", "convert", str(input_file), "--output", str(output_dir / "wechat.html"), *args_tail], str(MD2WECHAT_PROJECT), 60)
    if block_unsafe_command(command):
        return AdapterResult("md2wechat", str(MD2WECHAT_PROJECT), command.args, "blocked_unsafe", detail="Unsafe md2wechat command blocked.")
    if not input_file.exists():
        return AdapterResult("md2wechat", str(MD2WECHAT_PROJECT), command.args, "failed", detail="Input file does not exist.")
    if not (MD2WECHAT_PROJECT / "scripts" / "run.js").exists():
        return AdapterResult("md2wechat", str(MD2WECHAT_PROJECT), command.args, "unavailable", detail="scripts/run.js not found.")
    result = run_command(command)
    return AdapterResult(**{**result.to_dict(), "output_files": [str(output_dir / "wechat.html")]})
```

Implement the remaining adapters with the same pattern:

- `lint_md.py`: use `node -e` to verify local `package.json`; then mark `completed` only if a real runner is invoked.
- `textlint.py`: inspect local `package.json`; if no built CLI is available, return `unavailable` with project path.
- `zhlint.py`: run `node bin/index.js <input>` when `bin/index.js` exists.
- `wenyan.py`: inspect package scripts and return `unavailable` if no stable CLI is found.
- `markdown_nice.py`: read actual files `src/utils/converter.js` and `src/utils/styleMirror.css` when present, write a styled HTML wrapper, and return `completed`.

- [ ] **Step 4: Run adapter tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_adapters.py -v
```

Expected: PASS.

---

## Task 7: Package Orchestration Upgrade

**Files:**

- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py`
- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/report.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py`

- [ ] **Step 1: Write failing package contract test**

Create `test_open_source_package.py`:

```python
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"


class OpenSourcePackageTests(unittest.TestCase):
    def test_cli_writes_analysis_drafts_tool_results_reviews_and_upgraded_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            article = root / "script.md"
            article.write_text("# 标题\n\n> 核心定位：解释 AI 工作流。\n\n**口播：**\n\n这期视频讲 AI 工作流。\n", encoding="utf-8")
            out_dir = root / "out"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "article_publish.py"),
                    str(article),
                    "--out-dir",
                    str(out_dir),
                    "--deep-rewrite",
                    "--allow-external-tools",
                    "--media-plan",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            package = out_dir / "script"
            for relative in [
                "analysis/source-structure.json",
                "analysis/protected-spans.json",
                "analysis/content-diagnosis.md",
                "analysis/wechat-edit-plan.md",
                "analysis/zhihu-edit-plan.md",
                "drafts/wechat-deep-draft.md",
                "drafts/zhihu-deep-draft.md",
                "drafts/wechat-reviewed.md",
                "drafts/zhihu-reviewed.md",
                "reviews/editor-review.md",
                "reviews/platform-review.md",
                "tool-results/md2wechat.json",
                "tool-results/markdown-nice.json",
                "media/media-slots.json",
            ]:
                self.assertTrue((package / relative).exists(), relative)
            report = json.loads((package / "report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["editorial"]["deep_rewrite"])
            self.assertIn("tools", report)
            self.assertIn("quality_gates", report)
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py -v
```

Expected: CLI rejects `--deep-rewrite` or missing output files.

- [ ] **Step 3: Add CLI flags and orchestration**

Modify `article_publish.py`:

- add `--deep-rewrite`
- add `--render-motion` but keep default false
- create package subdirectories
- write source structure JSON and protected spans JSON
- write diagnosis and edit plans
- write deep drafts and reviewed drafts
- run adapter runner when `--allow-external-tools`
- write media slots JSON when `--media-plan`
- final render from reviewed drafts
- write upgraded report

- [ ] **Step 4: Run package test**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py -v
```

Expected: PASS.

---

## Task 8: Report and Checklist Consistency

**Files:**

- Modify: `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/report.py`
- Test: `/Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py`

- [ ] **Step 1: Write failing report consistency test**

Append:

```python
    def test_report_does_not_claim_tool_success_without_real_project_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            article = root / "script.md"
            article.write_text("# 标题\n\n正文。\n", encoding="utf-8")
            out_dir = root / "out"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "article_publish.py"),
                    str(article),
                    "--out-dir",
                    str(out_dir),
                    "--deep-rewrite",
                    "--media-plan",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            report = json.loads((out_dir / "script" / "report.json").read_text(encoding="utf-8"))
            for tool in report.get("tools", {}).values():
                if tool["status"] == "completed":
                    self.assertTrue(tool["used_real_project"])
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py -v
```

Expected: FAIL until upgraded report uses adapter data.

- [ ] **Step 3: Implement report contract**

Update `write_report` or add `write_upgraded_report` to include:

```python
"editorial": {
    "deep_rewrite": deep_rewrite,
    "diagnosis": "analysis/content-diagnosis.md",
    "wechat_plan": "analysis/wechat-edit-plan.md",
    "zhihu_plan": "analysis/zhihu-edit-plan.md",
    "status": "reviewed"
},
"tools": adapter_results,
"quality_gates": {
    "no_script_residue": "passed",
    "protected_spans_preserved": "passed",
    "toolchain_completed": "passed" if any_real_tool_completed else "partial",
    "subagent_review": "pending"
}
```

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest /Users/apulu/.codex/skills/article-publisher/tests/test_open_source_package.py -v
```

Expected: PASS.

---

## Task 9: Skill Documentation and Output Contract

**Files:**

- Modify: `/Users/apulu/.codex/skills/article-publisher/SKILL.md`
- Modify: `/Users/apulu/.codex/skills/article-publisher/references/output-contract.md`
- Modify: `/Users/apulu/.codex/skills/article-publisher/references/local-projects.md`
- Modify: `/Users/apulu/.codex/skills/article-publisher/references/platform-tools.md`

- [ ] **Step 1: Update SKILL.md workflow**

Update default workflow to include:

```text
source parse
-> protected spans
-> content diagnosis
-> platform edit plans
-> deep rewrite
-> open source adapters
-> media slots
-> Image Gen / Remotion briefs
-> final render
-> checklist/report
```

- [ ] **Step 2: Update output contract**

Add directories:

```text
analysis/
drafts/
tool-results/
reviews/
media/media-slots.json
media/remotion/render-status.json
```

- [ ] **Step 3: Update local project integration reference**

Document:

- approved install/build allowance
- read-only source modification boundary
- exact project paths
- adapter result statuses
- forbidden remote mutations

- [ ] **Step 4: Validate skill**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /Users/apulu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/apulu/.codex/skills/article-publisher
```

Expected: `Skill is valid!`

---

## Task 10: End-to-End Acceptance Run

**Files:**

- Output only under: `/Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite/`

- [ ] **Step 1: Run full test suite**

Run:

```bash
cd /Users/apulu/.codex/skills/article-publisher
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run full pipeline on target article**

Run:

```bash
rm -rf /Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite
mkdir -p /Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite
PYTHONDONTWRITEBYTECODE=1 python3 /Users/apulu/.codex/skills/article-publisher/scripts/article_publish.py \
  /Users/apulu/Documents/yy-article/write-v2/vibe-ai-problem-solving-video-script.md \
  --platform wechat \
  --platform zhihu \
  --out-dir /Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite \
  --cover /Users/apulu/Documents/yy-article/wx-output/cover-ai-vibe-workbench.png \
  --deep-rewrite \
  --allow-external-tools \
  --media-plan \
  --motion-plan
```

Expected: command exits `0` and prints package directory.

- [ ] **Step 3: Validate generated JSON**

Run:

```bash
pkg=/Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite/vibe-ai-problem-solving-video-script
python3 -m json.tool "$pkg/report.json" >/dev/null
python3 -m json.tool "$pkg/analysis/source-structure.json" >/dev/null
python3 -m json.tool "$pkg/analysis/protected-spans.json" >/dev/null
python3 -m json.tool "$pkg/media/media-slots.json" >/dev/null
```

Expected: no output and exit `0`.

- [ ] **Step 4: Validate no script residue**

Run:

```bash
pkg=/Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite/vibe-ai-problem-solving-video-script
rg -n "视频脚本版本|画面建议|屏幕字幕|拍摄备注|成片验收|成片主线|不要展示密钥|这期视频|整期视频" \
  "$pkg/wechat.md" "$pkg/wechat.html" "$pkg/zhihu.md" "$pkg/zhihu.html" "$pkg/canonical.md" "$pkg/polished.md"
```

Expected: `rg` exits `1` with no matches.

- [ ] **Step 5: Validate real tool reporting**

Run:

```bash
pkg=/Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite/vibe-ai-problem-solving-video-script
python3 - <<'PY'
import json
from pathlib import Path
pkg = Path("/Users/apulu/Documents/yy-article/skills-execute/article-publisher-open-source-deep-rewrite/vibe-ai-problem-solving-video-script")
report = json.loads((pkg / "report.json").read_text(encoding="utf-8"))
tools = report.get("tools", {})
required = {"lint-md", "textlint-wechat", "textlint-zhihu", "zhlint-wechat", "zhlint-zhihu", "md2wechat", "wenyan", "markdown-nice"}
missing = required - set(tools)
if missing:
    raise SystemExit(f"missing tools: {sorted(missing)}")
real = [name for name, value in tools.items() if value.get("used_real_project")]
if not real:
    raise SystemExit("no real open source project was used")
print("real tools:", ", ".join(sorted(real)))
PY
```

Expected: prints at least one real tool, preferably multiple.

- [ ] **Step 6: Run skill validation**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /Users/apulu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/apulu/.codex/skills/article-publisher
PYTHONDONTWRITEBYTECODE=1 python3 /Users/apulu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/apulu/.codex/skills/kazike-writing-style
```

Expected:

```text
Skill is valid!
Skill is valid!
```

- [ ] **Step 7: Subagent review**

Spawn review agents for:

- code/toolchain review
- final article quality review
- report/media consistency review

Expected: no blocking findings. If findings appear, fix with TDD and rerun relevant tests.

---

## Parallel Development Assignment

Use subagents with disjoint ownership:

1. Adapter worker:
   - owns `article_pipeline/adapters/*`
   - owns `tests/test_adapters.py`

2. Editorial worker:
   - owns `article_pipeline/editorial/*`
   - owns `source_structure.py`
   - owns `tests/test_editorial_pipeline.py`

3. Media/report worker:
   - owns `media.py`, `report.py`
   - owns `tests/test_media_slots.py`

4. Orchestration worker:
   - owns `article_publish.py`
   - owns `tests/test_open_source_package.py`

Main agent responsibilities:

- keep tests green
- integrate workers
- resolve conflicts
- run final target article
- run subagent reviews
- ensure final package under `skills-execute/`

---

## Self-Review Checklist

Spec coverage:

- Real local open source projects: covered by Tasks 6, 8, 10.
- Deep rewrite: covered by Tasks 3, 4, 7.
- Media slots and Image Gen/Remotion planning: covered by Task 5 and Task 10.
- Report/checklist/output package: covered by Tasks 7, 8, 9.
- TDD: every implementation task starts with failing tests.
- Subagents: assignment and final review are specified.
- Safety: unsafe md2wechat commands are blocked in Tasks 1 and 6.

No placeholders:

- No `TBD`, `TODO`, or unspecified "write tests" steps are used.
- Every task lists files and commands.

Git note:

- `/Users/apulu/Documents/yy-article` is not a git repository. This plan does not require commits in that directory.
- If `/Users/apulu/.codex/skills/article-publisher` is not a git repository, skip commit steps and record changed files in the final report.

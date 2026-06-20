# Article Publisher Open Source Deep Rewrite Design

## Goal

Upgrade `/Users/apulu/.codex/skills/article-publisher` from a lightweight local publishing package generator into a local article editing and publishing workbench.

The upgraded workflow accepts a Markdown video script or article draft and produces:

- a deeply rewritten WeChat article
- a deeply rewritten Zhihu article
- WeChat and Zhihu HTML previews
- image and motion media plans
- generated/reused local media assets
- real open source tool results
- a publish checklist
- a traceable `report.json`

The core product requirement is not only "format conversion". The pipeline must improve article quality: make the script clearer, deeper, more complete, easier to understand, and more platform-native.

## Confirmed Scope

The first upgraded version must use all of these local open source projects where technically possible:

- `/Users/apulu/Documents/yy-article/docs/projects/lint-md`
- `/Users/apulu/Documents/yy-article/docs/projects/textlint`
- `/Users/apulu/Documents/yy-article/docs/projects/textlint-rule-preset-zh-technical-writing`
- `/Users/apulu/Documents/yy-article/docs/projects/zhlint`
- `/Users/apulu/Documents/yy-article/docs/projects/md2wechat-skill`
- `/Users/apulu/Documents/yy-article/docs/projects/wenyan`
- `/Users/apulu/Documents/yy-article/docs/projects/markdown-nice`

The user explicitly approved local dependency installation and build commands for these project directories.

Allowed:

- install dependencies inside the local open source project directories
- build local packages
- run local CLI or script entry points
- create wrapper scripts inside `article-publisher`
- write generated execution artifacts under `/Users/apulu/Documents/yy-article/skills-execute/`

Forbidden by default:

- login
- upload images
- create WeChat or Zhihu drafts
- publish
- remote sync
- authenticated browser automation
- modifying upstream open source project source code unless a later explicit request allows it

## Recommended Approach

Use a two-chain architecture:

```text
Content chain:
source -> diagnosis -> platform edit plans -> deep rewrites -> editorial review

Tool chain:
source/deep drafts -> lint/adapters -> platform conversion -> styled HTML -> report
```

This balances quality and engineering reliability:

- LLM/Codex handles deep writing and editorial judgment.
- Python scripts handle deterministic parsing, protected spans, tool invocation, reports, and package assembly.
- Open source tools are real execution dependencies, not only reference names.
- Fallbacks remain available, but reports must never present a fallback as a successful open source integration.

## Architecture

The pipeline has four layers.

### 1. Source Intake

Responsibilities:

- parse Markdown
- extract title, summary, cover, images, links, headings, code fences, front matter
- identify video-script sections and labels
- identify protected spans
- copy existing local assets
- produce source structure artifacts

Outputs:

```text
analysis/source-structure.json
analysis/protected-spans.json
source-original.md
```

### 2. Editorial Engine

Responsibilities:

- diagnose the source
- create platform-specific edit plans
- produce deep WeChat and Zhihu drafts
- calibrate style using `kazike-writing-style`
- review for quality, fact preservation, platform fit, and script residue

Outputs:

```text
analysis/content-diagnosis.md
analysis/wechat-edit-plan.md
analysis/zhihu-edit-plan.md
analysis/style-calibration.md
drafts/wechat-deep-draft.md
drafts/zhihu-deep-draft.md
drafts/wechat-reviewed.md
drafts/zhihu-reviewed.md
reviews/editor-review.md
reviews/platform-review.md
```

### 3. Open Source Toolchain

Responsibilities:

- run real local tool adapters
- record command paths, project paths, stdout/stderr, output files, and fallback state
- keep remote-mutating commands blocked
- feed tool results back into checklist and report

Outputs:

```text
tool-results/lint-md.json
tool-results/textlint-wechat.json
tool-results/textlint-zhihu.json
tool-results/zhlint-wechat.json
tool-results/zhlint-zhihu.json
tool-results/md2wechat.json
tool-results/wenyan.json
tool-results/markdown-nice.json
```

### 4. Publish Package

Responsibilities:

- produce final platform files
- produce HTML previews
- produce and replace media assets
- produce checklist and report
- preserve a complete audit trail

Outputs:

```text
wechat.md
wechat.html
zhihu.md
zhihu.html
canonical.md
polished.md
assets/
media/
publish-checklist.md
report.json
```

## Proposed Code Structure

Inside `/Users/apulu/.codex/skills/article-publisher/scripts/article_pipeline/`:

```text
adapters/
├── base.py
├── lint_md.py
├── textlint.py
├── zhlint.py
├── md2wechat.py
├── wenyan.py
└── markdown_nice.py

editorial/
├── diagnosis.py
├── planning.py
├── deep_rewrite.py
├── review.py
└── schemas.py
```

Keep existing modules for parsing, checking, assets, renderers, media, reports, and tools. Refactor only where required to support the new architecture.

## Adapter Contract

Every adapter implements the same conceptual sequence:

```text
discover()
prepare()
run(input, output)
collect()
```

Every adapter writes structured output shaped like:

```json
{
  "name": "lint-md",
  "project_path": "/Users/apulu/Documents/yy-article/docs/projects/lint-md",
  "command": "...",
  "status": "completed",
  "used_real_project": true,
  "output_files": [],
  "stdout_tail": "",
  "stderr_tail": "",
  "fallback_used": false
}
```

Allowed statuses:

- `completed`
- `unavailable`
- `failed`
- `skipped`
- `blocked_unsafe`

Adapter rules:

- If the local project is unavailable, record `unavailable`.
- If the local project exists but fails, record `failed`.
- If a fallback renderer is used, record `fallback_used = true`.
- If the adapter actually invokes or reads the local project, record `used_real_project = true`.
- If a command is remote-mutating, block it and record `blocked_unsafe`.
- Truncate stdout/stderr in JSON to avoid noisy reports.

## Tool-Specific Adapter Design

### lint-md

Purpose: Markdown and Chinese formatting checks.

Project path:

```text
/Users/apulu/Documents/yy-article/docs/projects/lint-md
```

Execution priority:

1. Install/build if needed.
2. Use a stable JS API if build artifacts expose one.
3. Otherwise create an `article-publisher` wrapper that imports the local source/build output.
4. If no stable local execution path exists, record `unavailable`, not success.

Outputs:

```text
tool-results/lint-md.json
logs/lint-md.log
```

### textlint and zh technical writing preset

Purpose: Chinese technical writing diagnostics.

Project paths:

```text
/Users/apulu/Documents/yy-article/docs/projects/textlint
/Users/apulu/Documents/yy-article/docs/projects/textlint-rule-preset-zh-technical-writing
```

Execution:

- install/build local projects if needed
- generate temporary `.textlintrc`
- run on `drafts/wechat-reviewed.md`
- run on `drafts/zhihu-reviewed.md`
- report only by default; no automatic fixes in version 1

Outputs:

```text
tool-results/textlint-wechat.json
tool-results/textlint-zhihu.json
```

### zhlint

Purpose: additional Chinese linting for punctuation, spacing, and prose style.

Project path:

```text
/Users/apulu/Documents/yy-article/docs/projects/zhlint
```

Execution:

- install/build if needed
- run local `bin/index.js` or built equivalent
- report only by default

Outputs:

```text
tool-results/zhlint-wechat.json
tool-results/zhlint-zhihu.json
```

### md2wechat

Purpose: WeChat-specific conversion, preview, and HTML generation.

Project path:

```text
/Users/apulu/Documents/yy-article/docs/projects/md2wechat-skill
```

Allowed commands:

- `doctor`
- `inspect`
- `preview`
- `convert --output`

Forbidden commands:

- upload
- draft
- publish
- login
- image upload
- remote sync

Output priority:

- If md2wechat conversion succeeds, `wechat.html` should use it.
- Python fallback HTML can be kept as `wechat-fallback.html`.

Outputs:

```text
tool-results/md2wechat.json
wechat.html
```

### Wenyan

Purpose: multi-platform Markdown/HTML adaptation, especially WeChat/Zhihu differences.

Project path:

```text
/Users/apulu/Documents/yy-article/docs/projects/wenyan
```

Execution:

- inspect for CLI/core package availability
- build only if local scripts expose a safe local artifact
- do not modify app source
- if only macOS app/web flows are present with no stable local CLI, record `unavailable`

Outputs when available:

```text
wechat-wenyan.md
wechat-wenyan.html
zhihu-wenyan.md
zhihu-wenyan.html
tool-results/wenyan.json
```

### markdown-nice

Purpose: theme/style reference and styled HTML generation.

Project path:

```text
/Users/apulu/Documents/yy-article/docs/projects/markdown-nice
```

Execution:

- prefer stable converter/theme assets from the project
- if there is no CLI, real usage can be satisfied by reading actual theme/style/converter files and generating styled HTML from those assets
- report exact files read from the project

Outputs:

```text
wechat-nice.html
zhihu-nice.html
tool-results/markdown-nice.json
```

## Deep Editorial Workflow

### Content Diagnosis

Create:

```text
analysis/content-diagnosis.md
```

The diagnosis must answer:

- What is the core thesis?
- Which parts are video production instructions?
- Which parts are usable spoken content?
- Which parts need deeper explanation?
- Which parts are vague or slogan-like?
- Which parts need cases, boundaries, or counterexamples?
- Where should images or motion assets appear?
- What will block WeChat readers?
- What will block Zhihu readers?

### Platform Edit Plans

Create:

```text
analysis/wechat-edit-plan.md
analysis/zhihu-edit-plan.md
```

The WeChat plan emphasizes:

- scene-setting
- short paragraphs
- story flow
- concrete analogies
- emotional pacing
- action-oriented ending

The Zhihu plan emphasizes:

- clear upfront conclusion
- definitions
- logic chain
- counterexamples
- boundaries
- actionable steps

Edit plans must be section-level and specific, not generic advice.

### Deep Rewrite

Create:

```text
drafts/wechat-deep-draft.md
drafts/zhihu-deep-draft.md
```

Rules:

- preserve facts
- preserve project names
- preserve code, commands, links, numbers, and technical terms
- remove video-production scaffolding
- rewrite into independently readable articles
- expand explanation only from source-supported logic
- do not invent cases, numbers, roles, external endorsements, or evidence

### Style Calibration

Use `kazike-writing-style` as a method guide, not a sentence template.

Calibrate for:

- event scene
- practitioner perspective
- process evidence
- failure details
- mechanism explanation
- trend judgment
- ordinary-reader action

Create:

```text
analysis/style-calibration.md
drafts/wechat-reviewed.md
drafts/zhihu-reviewed.md
```

If source data is missing, record what is missing. Do not invent it.

### Editorial Review

Create:

```text
reviews/editor-review.md
reviews/platform-review.md
```

Review gates:

- no script residue
- no unsupported claims
- no empty slogans
- each abstract idea has explanation, case, or boundary
- WeChat and Zhihu structures are meaningfully different
- platform tone fits
- media slots are sufficient
- protected spans are preserved

If review fails, final rendering must not proceed.

## Media Design

Replace fixed one-image behavior with structure-driven media planning.

Create:

```text
media/media-slots.json
media/image-prompts.json
media/motion-plan.json
media/media-plan.md
```

Slot example:

```json
{
  "id": "figure-01-overview",
  "platforms": ["wechat", "zhihu"],
  "type": "image",
  "insert_after_heading": "开场：AI 时代第一生产资料",
  "purpose": "解释全文核心问题解决闭环",
  "source_excerpt": "AI 不是替你省掉思考，而是让你用更高吞吐完成探索、生成、反驳、执行和验收。",
  "required": true,
  "executor": "imagegen",
  "status": "planned"
}
```

Default quantity rules:

- under 1000 Chinese characters: cover plus 1 inline image
- 1000-3000 characters: cover plus 2 inline images
- 3000-6000 characters: cover plus 3-5 inline images
- over 6000 characters: cover plus 1 image per 1200-1800 characters
- methodology articles must include an overview image, a flow image, and a comparison image
- complex workflows should include one motion plan

For the Vibe methodology article, expected media slots are:

- cover
- `figure-01-overview`: AI problem-solving loop overview
- `figure-02-research-map`: unknown-domain research map
- `figure-03-agent-parallel`: multi-agent workbench
- `figure-04-verification-loop`: dual-model review and verification loop
- `motion-01-loop`: 8-second loop animation brief

Image Gen flow:

```text
media-slots.json
-> image-prompts.json
-> imagegen skill
-> assets/
-> replace placeholders
-> report.json
```

Remotion flow:

```text
media/remotion/motion-plan.json
media/remotion/storyboard.md
media/remotion/props.json
media/remotion/render-status.json
```

Default status is `brief_only`. Only generate GIF/MP4 when a later explicit `--render-motion` or user instruction asks for it.

## Output Package Contract

The upgraded package root is:

```text
<out-dir>/<slug>/
├── source-original.md
├── canonical.md
├── polished.md
├── wechat.md
├── wechat.html
├── zhihu.md
├── zhihu.html
├── assets/
├── analysis/
├── drafts/
├── media/
├── tool-results/
├── reviews/
├── logs/
├── publish-checklist.md
└── report.json
```

Detailed package shape:

```text
analysis/
├── source-structure.json
├── protected-spans.json
├── content-diagnosis.md
├── wechat-edit-plan.md
├── zhihu-edit-plan.md
└── style-calibration.md

drafts/
├── wechat-deep-draft.md
├── zhihu-deep-draft.md
├── wechat-reviewed.md
└── zhihu-reviewed.md

media/
├── media-slots.json
├── image-prompts.json
├── media-plan.md
└── remotion/
    ├── motion-plan.json
    ├── storyboard.md
    ├── props.json
    └── render-status.json

tool-results/
├── lint-md.json
├── textlint-wechat.json
├── textlint-zhihu.json
├── zhlint-wechat.json
├── zhlint-zhihu.json
├── md2wechat.json
├── wenyan.json
└── markdown-nice.json

reviews/
├── editor-review.md
├── platform-review.md
└── subagent-review.md
```

## Report Contract

`report.json` must include:

```json
{
  "source": {},
  "platforms": ["wechat", "zhihu"],
  "editorial": {
    "deep_rewrite": true,
    "diagnosis": "analysis/content-diagnosis.md",
    "wechat_plan": "analysis/wechat-edit-plan.md",
    "zhihu_plan": "analysis/zhihu-edit-plan.md",
    "status": "reviewed"
  },
  "tools": {
    "lint-md": {
      "used_real_project": true,
      "status": "completed",
      "project_path": "/Users/apulu/Documents/yy-article/docs/projects/lint-md"
    }
  },
  "media": {
    "required_slots": 5,
    "generated": 4,
    "brief_only": 1,
    "unresolved": 0
  },
  "quality_gates": {
    "no_script_residue": "passed",
    "protected_spans_preserved": "passed",
    "toolchain_completed": "passed",
    "subagent_review": "passed"
  }
}
```

The report must not claim success for a tool or generated media asset unless that action actually happened.

## Checklist Contract

`publish-checklist.md` must cover:

- title
- summary
- cover
- first image
- inline image count
- local image existence
- links
- code fences
- protected spans
- deep rewrite completion
- platform tone checks
- lint results
- converter results
- media slot results
- subagent review
- actions not performed: upload, draft, publish, sync

## Quality Gates

Hard gates:

- `wechat.md`, `wechat.html`, `zhihu.md`, `zhihu.html` exist.
- no video-script operational labels remain in final files.
- all referenced local images exist.
- all required media slots are resolved or explicitly downgraded with reason.
- lint-md, textlint, and zhlint completed or recorded real failure reasons.
- md2wechat performed at least one safe WeChat conversion/preview or recorded real failure reason.
- markdown-nice read real project theme/style/converter files and produced styled HTML or recorded real failure reason.
- Wenyan either produced platform artifacts or recorded why no stable local CLI was available.
- subagent review passed.
- report states match actual files.

Soft gates:

- WeChat opening has scene and momentum.
- Zhihu opening has a clear conclusion.
- abstract ideas include explanation, case, or boundary.
- platform structures differ meaningfully.
- images match nearby text.
- no template-like filler.
- the article can be read independently without video context.

## Failure Handling

External tool failure does not crash the whole package.

On failure:

- write `tool-results/<tool>.json`
- mark status as `failed` or `unavailable`
- keep fallback output if available
- add checklist item
- reflect fallback in `report.json`

The upgraded workflow cannot pass final acceptance if all key open source integrations are unavailable or skipped.

## Testing Strategy

Use TDD for implementation.

Required tests:

- adapter unavailable behavior
- adapter failed behavior
- adapter success behavior with `used_real_project = true`
- unsafe command blocking for md2wechat
- stale assets cleanup
- source structure generation
- protected span preservation
- content diagnosis task generation
- platform edit plan artifacts
- deep rewrite artifacts present
- script residue removed
- media slot quantity rules
- media placeholder replacement
- report consistency with actual files
- package output contract
- validation of both skills

Subagent review is required before final acceptance.

## Acceptance Scenario

Run the upgraded pipeline on:

```text
/Users/apulu/Documents/yy-article/write-v2/vibe-ai-problem-solving-video-script.md
```

Expected:

- output under `/Users/apulu/Documents/yy-article/skills-execute/`
- deep WeChat and Zhihu drafts are meaningfully different
- final article quality is better than the current version
- at least 3-5 image/motion slots are planned
- key required images are generated or reused
- real open source tool adapters run and are recorded
- report/checklist/media plans are self-consistent
- subagent review says the output can be published

## Commit Note

The working directory `/Users/apulu/Documents/yy-article` is not currently a git repository, so the design document cannot be committed there without initializing or selecting another repository. Do not initialize a repository as part of this brainstorming step.

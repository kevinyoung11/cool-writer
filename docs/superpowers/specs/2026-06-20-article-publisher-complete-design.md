# Article Publisher Complete Design

## Goal

Upgrade `/Users/apulu/.codex/skills/article-publisher` from a static checklist helper into a local publish-package pipeline for Chinese Markdown articles. The pipeline accepts one Markdown file and produces checked, platform-specific, manually publishable WeChat Official Account and Zhihu outputs, plus media briefs for Image Gen and Remotion.

## Scope

Version 1 is local and non-destructive by default.

It must generate:

- canonical Markdown
- optionally polished Markdown when the agent performs style work
- WeChat Markdown
- WeChat HTML
- Zhihu Markdown
- publish checklist
- machine-readable report JSON
- media plan with cover, inline image, and optional motion briefs
- tool availability log

It must not:

- upload images
- push WeChat drafts
- publish to any platform
- sync through browser extensions
- replace local image paths with remote URLs
- rewrite code blocks, inline code, links, numbers, project names, or quoted prompts during formatting

## Inputs

Required:

- `article.md`

Optional CLI flags:

- `--platform wechat`
- `--platform zhihu`
- `--out-dir DIR`
- `--slug SLUG`
- `--title TITLE`
- `--summary TEXT`
- `--cover PATH`
- `--fix-lint`
- `--media-plan`
- `--motion-plan`
- `--allow-external-tools`

`--allow-external-tools` permits safe local converter/linter commands, but still excludes upload, draft, publish, and sync commands.

## Output Contract

For input `article.md`, output goes to:

```text
<out-dir>/<slug>/
├── canonical.md
├── polished.md
├── wechat.md
├── wechat.html
├── zhihu.md
├── publish-checklist.md
├── report.json
├── media/
│   ├── media-plan.md
│   ├── image-prompts.json
│   └── motion-brief.md
└── logs/
    ├── lint.json
    └── tool-availability.json
```

If no polish step is performed, `polished.md` equals `canonical.md` and the report records `polish.status = "not_requested"`.

## Architecture

The implementation is a small Python package inside the skill scripts directory:

- `article_publish.py`: CLI entry point and orchestration.
- `article_pipeline/markdown.py`: Markdown parsing, metadata extraction, protected-span helpers, slug generation.
- `article_pipeline/checks.py`: static checks for titles, images, links, code fences, placeholders, summary, cover, and platform reminders.
- `article_pipeline/renderers.py`: deterministic WeChat Markdown/HTML and Zhihu Markdown renderers.
- `article_pipeline/tools.py`: local tool discovery and safe command wrappers.
- `article_pipeline/media.py`: Image Gen and Remotion brief generation.
- `article_pipeline/report.py`: checklist, JSON report, and package manifest creation.

Tests live in `/Users/apulu/.codex/skills/article-publisher/tests`.

## Platform Behavior

### WeChat

The WeChat Markdown keeps source structure but adds a compact metadata block only when useful for manual publishing. WeChat HTML uses conservative inline CSS and readable article markup. It must keep code blocks intact and escape HTML.

The checklist must include title, cover, summary, images, external links, and manual preview reminders.

### Zhihu

The Zhihu Markdown stays close to plain Markdown. It removes WeChat-only operational notes when the section is clearly marked as WeChat-only. It keeps local image paths for manual upload workflows.

### Multi-Platform

Canonical content is copied first. Platform renderers write separate files and never mutate the canonical file.

## Tool Boundaries

Safe default:

- Python-only parser, checker, renderers, and media brief generation.
- No network requirements.
- No credentials.

Safe optional external use:

- `md2wechat inspect`
- `md2wechat preview`
- `lint-md` or local lint-md core wrappers
- `textlint` report-only
- `zhlint` report-only

Forbidden unless explicitly requested in a future publish command:

- `md2wechat convert --draft`
- image upload commands
- WeChat material upload
- Wechatsync publishing/sync
- browser automation that changes remote drafts

## Media Stage

The script can generate deterministic media briefs:

- cover image prompt
- 2-4 inline illustration prompts
- image usage/order list
- Remotion motion brief for a short GIF or article teaser

The Codex skill instructions will tell the agent to use Image Gen only after the script has produced prompts and only when the user requested generated visuals. Remotion output is also explicit: the script creates a brief and file structure, while a later agent step can scaffold or render a Remotion project.

## Error Handling

Missing local images, broken links, multiple H1 titles, unbalanced fences, placeholder text, missing summary, and missing cover are checklist blockers or warnings, not crashes.

The CLI exits non-zero only when:

- the input file is missing
- the input file cannot be decoded
- the output directory cannot be written
- an internal renderer error occurs

External tool failures are recorded in `logs/tool-availability.json` and `report.json`, and the Python fallback output is still generated.

## Acceptance Criteria

- Given a valid Markdown file with title, summary, cover, images, links, and code, the command produces every file in the output contract.
- Given a Markdown file with missing local images and placeholders, the checklist and `report.json` contain those findings.
- Code fences and inline code are unchanged in platform Markdown outputs.
- WeChat HTML contains escaped code blocks and basic article styling.
- Zhihu Markdown is plain Markdown and does not contain generated HTML.
- Media plan contains at least one cover prompt and one motion brief when requested.
- Running tests from the skill directory passes.
- Running the pipeline on a sample article under `/Users/apulu/Documents/yy-article` succeeds without external tools installed.
- The skill validation script passes for the final skill folder.

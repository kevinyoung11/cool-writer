# article-publisher v2 设计

生成时间：2026-06-21

## 0. 范围（与 codex-1st-round.md 的纠偏）

`codex-1st-round.md` 解的是「想法+素材 → 生成脚本」（生成型，推荐 LangGraph/向量库/Promptfoo）。
本项目真实场景是「**已有脚本/文章 → 润色 → 改写成微信公众号 + 知乎可发布版**」（改写/排版/发布型），
以 **skill** 形式落地。两者难点不同，故 codex 方案归档，不作为 v2 依据。

本设计以 v1（`design/v1/talk-v1.md` 的「确定性工具链 + LLM 深度编辑链」两条线）为基线增量实现。

## 1. 架构

```
源脚本(.md)
  └─[LLM 编辑链]  诊断 → 深度改写 → 风格对齐 → 说人话      → wechat.md / zhihu.md
  └─[确定性管线]  canonical → lint(OSS) → wenyan 排版(OSS) → 保真度校验 → report + checklist
```

- **LLM 编辑链**：味道、平台差异、风格对齐（接 `kazike-writing-methodology-lite.md`）。见 SKILL.md 阶段 1–2。
- **确定性管线**：`article-publisher/skill/scripts/run_pipeline.py`。可验证、可复现。

目录：
```
article-publisher/skill/
├── SKILL.md                  # LLM 编辑链 + 调用方式
├── config/defaults.json      # 工具注册表、路径、wenyan 主题
├── config/.textlintrc.json   # textlint 中文技术写作规则
├── scripts/adapters.py       # OSS 工具适配层（discover→can_run→run→collect）
├── scripts/fidelity.py       # 保真度程序化校验
├── scripts/run_pipeline.py   # 管线编排
└── tools/                    # 本地 OSS 工具箱（npm，已锁版本）
article-publisher/runs/<slug>/ # 每篇文章的产物
```

## 2. 关键决策

### 2.1 用「已发布的 npm 包」而非重建 vendored 源码
`docs/projects/` 里的 lint-md / zhlint / textlint 都是 **未构建的 TS 源码**（缺 `lib/`，
装机时跑 `tsc` 失败），逐个 build 是 pnpm workspace + monorepo 的深坑。
改为在 `tools/package.json` 锁定 **官方已构建包**：
`@lint-md/cli` / `zhlint` / `textlint` + `textlint-rule-preset-zh-technical-writing`。
可复现、可一键重装。

### 2.2 wenyan 用 `@wenyan-md/cli`，不是 vendored 的 macOS app
`docs/projects/wenyan` 是 `@wenyan-md/mac`（xcodebuild 的桌面 app），不是 CLI。
正确 CLI 是 npm 上的 `@wenyan-md/cli`（`wenyan render` 输出**内联样式 HTML**，
正好能粘进公众号编辑器），**一个工具同时覆盖公众号 + 知乎**双平台。

### 2.3 适配层契约：discover → can_run → run → collect
`can_run` 是**真实健康检查**（bin 解析 + `--version/--help` 探针），不再是占位。
旧实现里 lint-md 是个只数字节的假 `node -e`——本版删除，换成真 lint。

### 2.4 显式降级
工具跑不了时，记录 `status=unavailable/failed` + `fallback_used`，并在
`publish-checklist.md` 的「降级提示」里列出，让人知道哪份产物是降级的、需人工复核。

### 2.5 保真度做成程序化、确定性
改写最大风险是悄悄改/丢数字、术语、代码、链接。`fidelity.py` 从 canonical 抽取
**真代码 fence（按语言标签判定，排除 ```text 散文/示意图）、内联代码、URL、有意义数字
（带单位或 ≥3 位）**，逐项在改写稿里 diff。任何缺失 = checklist 标 ❌，回改重跑。
不依赖 LLM 自评。

### 2.6 不引入 LangGraph
这是确定性管线 + 几个 LLM 节点的线性流程，Python 编排足够。LangGraph 仅在需要
「按评分自动回退循环」时才值得——改写场景人工卡点比自动回退更合适。

## 3. 验收（已通过，2026-06-21）

在 `write-v2/vibe-ai-problem-solving-video-script.md` + 既有平台稿上端到端运行：

- 工具健康：`lint-md / zhlint / textlint / wenyan` 全部 `available: true`
  （对比改造前 report.json：11 次工具调用 9 次 failed/skipped，且唯一“成功”的 lint-md 是假的）。
- 真实 OSS 工具成功次数：**11**。
- 产物齐全：canonical、wechat/zhihu 的 md+html（wenyan 内联样式 ~20KB）、
  lint 结果、fidelity 报告、report.json、publish-checklist.md。
- 保真度真起作用：捕获到改写稿丢失原文「省了 **500** 字」的数字（真阳性），
  并在 checklist 标 ❌ 提示人工复核。
- 脏输入回归：故意构造中英文混排/英文标点，lint-md 报 1 项、textlint 报 3 项——
  证明 linter 做真活，非空跑。

## 4. 后续可做（非阻塞）
- 风格对齐节点固化为可检条目（句长分布、术语表、口吻样本检索）。
- 平台合规项部分可程序化（如检测“点击上方关注”等微信专用话术后在知乎稿告警）。
- 知乎代码/公式渲染差异的针对性校验。
- 把好稿/差稿样本接入，做 LLM-judge 质量评分（可选，用 Promptfoo 做 prompt 回归）。

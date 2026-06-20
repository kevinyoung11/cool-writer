要真正做到两件事：

1. **真的用上开源项目的能力**
2. **把视频脚本改得深入浅出、完整、优秀**

不能只靠现在这个 Python 规则脚本。应该把 skill 拆成“确定性工具链 + LLM 深度编辑链”两条线。

**一、工具链怎么真正用开源项目**

应该把本地开源项目接成 adapter，而不是只写 reference。

建议做这些 adapter：

```text
article_pipeline/adapters/
├── lint_md.py
├── textlint.py
├── zhlint.py
├── md2wechat.py
├── wenyan.py
├── markdown_nice.py
└── remotion.py
```

每个 adapter 做四件事：

```text
discover -> can_run -> run -> collect_result
```

例如：

- `lint-md`：检查中文标点、空格、标题、列表、链接格式。
- `textlint`：检查技术写作问题、病句、冗余表达。
- `zhlint`：补充中文风格检查。
- `md2wechat`：生成更接近公众号编辑器的 HTML。
- `markdown-nice`：复用主题样式、代码块、引用、图片样式。
- `Wenyan`：做多平台 Markdown 转换。
- `Remotion`：基于 media brief 真正生成 GIF/MP4，而不是只写 brief。

`report.json` 里要记录：

```json
{
  "tools_used": [
    {
      "name": "lint-md",
      "project": "/Users/apulu/Documents/yy-article/docs/projects/lint-md",
      "command": "...",
      "status": "completed"
    }
  ]
}
```

这样才算“真的用到了开源项目”。

**二、深度改写不能放在普通脚本里硬写**

现在最大的问题是：`rewriter.py` 用模板改写。模板适合清理，不适合写出好文章。

正确做法是新增一个“编辑阶段”，让 LLM 负责深度改写，但脚本负责结构和验收。

流程应该变成：

```text
原始视频脚本
-> 结构解析
-> 内容诊断
-> 微信编辑计划
-> 知乎编辑计划
-> 深度改写
-> 风格校准
-> 事实/术语保护
-> 配图规划
-> 工具链排版
-> 质量复审
-> 最终发布包
```

其中最关键的是新增这些中间产物：

```text
analysis/content-diagnosis.json
analysis/wechat-edit-plan.md
analysis/zhihu-edit-plan.md
drafts/wechat-deep-draft.md
drafts/zhihu-deep-draft.md
reviews/editor-review.md
reviews/platform-review.md
```

**三、内容诊断要先做**

改写前必须先回答：

- 这篇文章真正的主张是什么？
- 哪些内容只是口播废话？
- 哪些地方读者看不懂？
- 哪些概念需要补例子？
- 哪些判断需要补论据？
- 哪些段落可以删？
- 哪些段落应该扩？
- 哪些地方适合做图？
- 微信读者怎么读？
- 知乎读者怎么读？

没有这一步，改写只能是“换口吻”，不是“提升质量”。

**四、微信和知乎应该分开编辑**

微信公众号稿：

```text
现场感更强
短段落
强开头
多转折
多比喻
多案例
结尾有行动感
```

知乎稿：

```text
先结论
概念定义更清楚
论证链更完整
边界条件更多
反例更多
少一点情绪，多一点解释
```

不能只是同一篇文章换个开头。

**五、卡兹克风格要变成编辑规则，不是模板句**

不要固定写：

```text
最近我反复看到一个现象……
```

而是用它的方法论：

```text
事件现场 -> 个人实践 -> 过程数字 -> 失败细节 -> 机制解释 -> 趋势判断 -> 普通人行动
```

这才是“结合风格”。

**六、配图数量要由文章结构决定**

建议规则：

```text
封面：1 张
总览图：1 张
每 1200-1800 字：1 张解释图
方法论文章：至少 3 张图
复杂流程文章：至少 1 个动图 brief
```

对这篇 AI 方法论文章，合理配图应该是：

1. 封面图
2. AI 问题解决总览图
3. 未知领域调研流程图
4. 多 agent 并行工作图
5. 验收/反驳闭环图
6. 可选 Remotion 动图：问题解决循环

**七、验收标准要提高**

现在的验收是“没有残留、文件存在”。以后应该加内容质量验收：

```text
主论点清晰
每个大段都有推进
没有脚本腔
没有空泛口号
每个抽象概念都有例子
每个平台稿有不同结构
图片数量匹配文章长度
配图都被正文引用
工具链结果可追溯
子任务复审通过
```

一句话：  
现在的 skill 是“发布包生成器”；你想要的是“平台文章编辑部 + 开源排版工具链”。下一步要把它升级成：**工具负责格式和检测，LLM 负责深度编辑，subagent 负责复审，report 负责可追溯**。


---

**设计 1：目标与边界**

这次升级的目标不是再做一个轻量转换脚本，而是把 `article-publisher` 升级成一个“本地文章编辑发布工作台”。

核心目标：

```text
输入：Markdown 视频脚本或文章草稿
输出：微信公众号终稿、知乎终稿、对应 HTML、配图/动图计划、真实工具检查报告、发布 checklist
```

必须做到：

- 真实调用本地开源项目：`lint-md`、`textlint`、`textlint-rule-preset-zh-technical-writing`、`zhlint`、`md2wechat`、`Wenyan`、`markdown-nice`。
- 自动深度改写：不是模板改写，而是先诊断，再生成平台编辑计划，再生成微信/知乎两篇深度稿。
- 改写要深入浅出：保留事实、项目名、技术细节、代码块、链接，同时增强解释、案例、结构、转折、结论和行动建议。
- 配图数量按文章结构决定，不再固定 1 张图。
- 所有工具调用、失败、fallback、人工替换、Image Gen 产物都进入 `report.json`。
- 所有执行目录仍放在 `~/Documents/yy-article/skills-execute/` 下。

明确不做：

- 不登录公众号/知乎。
- 不上传图片。
- 不推草稿箱。
- 不发布。
- 不使用 Wechatsync 做远程同步。
- 不修改开源项目源码，除非构建必须且你后续明确允许；本轮只允许安装/构建/本地只读调用。

第一版成功标准：

- 同一篇视频脚本能产出明显优于当前版本的微信/知乎稿。
- report 能证明哪些开源项目被真实调用。
- 至少生成 3-5 个图片/动图候选位，并实际生成/替换关键图片。
- 复审结论是“可发布”，而不是“只是格式正确”。

这块边界对吗？确认后我继续给架构设计。

---

**设计 2：总体架构**

推荐改成四层流水线。

```text
1. Source Intake
   解析原文、front matter、标题、摘要、封面、图片、链接、代码块、视频脚本结构

2. Editorial Engine
   内容诊断
   -> 微信编辑计划
   -> 知乎编辑计划
   -> 微信深度稿
   -> 知乎深度稿
   -> 编辑复审

3. Open Source Toolchain
   lint-md / textlint / zhlint
   -> md2wechat
   -> Wenyan
   -> markdown-nice 样式/主题参考
   -> 输出工具报告和 fallback 结果

4. Publish Package
   assets
   -> wechat.md / wechat.html
   -> zhihu.md / zhihu.html
   -> media plan / image prompts / motion brief
   -> checklist / report.json
```

建议目录结构：

```text
article_pipeline/
├── adapters/
│   ├── base.py
│   ├── lint_md.py
│   ├── textlint.py
│   ├── zhlint.py
│   ├── md2wechat.py
│   ├── wenyan.py
│   └── markdown_nice.py
├── editorial/
│   ├── diagnosis.py
│   ├── planning.py
│   ├── deep_rewrite.py
│   ├── review.py
│   └── schemas.py
├── media.py
├── renderers.py
├── report.py
└── article_publish.py
```

新增中间产物：

```text
analysis/
├── source-structure.json
├── content-diagnosis.md
├── wechat-edit-plan.md
├── zhihu-edit-plan.md
└── protected-spans.json

drafts/
├── wechat-deep-draft.md
├── zhihu-deep-draft.md
├── wechat-reviewed.md
└── zhihu-reviewed.md

tool-results/
├── lint-md.json
├── textlint.json
├── zhlint.json
├── md2wechat.json
├── wenyan.json
└── markdown-nice.json
```

核心原则：

- **脚本不负责写好文章**：脚本负责生成诊断材料、保护约束、调用工具、保存产物。
- **LLM 负责深度编辑**：但必须输出结构化文件，不能只在对话里改。
- **开源工具必须真实执行**：成功、失败、fallback 都记录。
- **平台稿是主线**：后续配图、HTML、lint、report 都基于微信/知乎深度稿，而不是原始视频脚本。
- **fallback 可以存在，但不能冒充成功**：如果 `Wenyan` 或 `markdown-nice` 不可用，报告必须写清楚没有真实使用。

数据流：

```text
source.md
-> source-structure.json
-> content-diagnosis.md
-> wechat-edit-plan.md / zhihu-edit-plan.md
-> wechat-deep-draft.md / zhihu-deep-draft.md
-> lint/adapters
-> platform converters
-> media planning + Image Gen prompts
-> final package
-> subagent review
```

这块架构对吗？确认后我继续给“开源工具 adapter 设计”，会具体到每个项目怎么真实调用、失败怎么处理。

---

**设计 3：开源工具 Adapter**

每个开源项目都用统一 adapter 协议：

```text
discover()
prepare()
run(input, output)
collect()
```

统一输出：

```json
{
  "name": "lint-md",
  "project_path": "...",
  "command": "...",
  "status": "completed | unavailable | failed | skipped",
  "used_real_project": true,
  "output_files": [],
  "stdout_tail": "",
  "stderr_tail": "",
  "fallback_used": false
}
```

**1. lint-md**

目标：检查 Markdown 和中文排版问题。

真实使用方式：

- 项目路径：`docs/projects/lint-md`
- 允许：安装依赖、build
- 调用方式优先级：
  1. 如果 build 后有可用 JS API，用 Node wrapper 调用 `@lint-md/core`
  2. 如果没有稳定 API，就调用项目测试/核心入口包装一个本地 runner
  3. 失败则记录 unavailable，不冒充成功

输出：

```text
tool-results/lint-md.json
logs/lint-md.log
```

**2. textlint + textlint-rule-preset-zh-technical-writing**

目标：检查中文技术写作、冗余表达、术语、标点、句式问题。

真实使用方式：

- 项目路径：
  - `docs/projects/textlint`
  - `docs/projects/textlint-rule-preset-zh-technical-writing`
- 允许本地 install/build
- 生成临时 `.textlintrc`
- 对 `wechat-deep-draft.md` 和 `zhihu-deep-draft.md` 分别跑
- 不自动改正文，先只产出 findings；自动修复需要单独开关

输出：

```text
tool-results/textlint-wechat.json
tool-results/textlint-zhihu.json
```

**3. zhlint**

目标：补充中文语言和标点检查。

真实使用方式：

- 项目路径：`docs/projects/zhlint`
- build 后调用 `bin/index.js`
- 只做 report，不直接改稿

输出：

```text
tool-results/zhlint-wechat.json
tool-results/zhlint-zhihu.json
```

**4. md2wechat**

目标：生成更接近公众号编辑器的 HTML/预览结果。

真实使用方式：

- 项目路径：`docs/projects/md2wechat-skill`
- 调用 `scripts/run.js`
- 只允许安全命令：
  - `doctor`
  - `inspect`
  - `preview`
  - `convert --output`
- 禁止：
  - upload
  - draft
  - publish
  - login
  - image upload

输出：

```text
wechat.md
wechat.html
tool-results/md2wechat.json
```

如果 md2wechat 输出成功，`wechat.html` 优先用它；Python fallback 作为 `wechat-fallback.html` 保留。

**5. Wenyan**

目标：多平台 Markdown/HTML 适配，尤其知乎/公众号平台差异。

真实使用方式：

- 项目路径：`docs/projects/wenyan`
- 先检查是否有 CLI/core package 可调用
- 如果只有 macOS app/web build，不强行改项目源码
- 可用则生成：
  - `wechat-wenyan.md/html`
  - `zhihu-wenyan.md/html`
- 如果不可用，报告里明确 `unavailable: no stable local CLI found`

注意：Wenyan 真实集成以“能跑它的本地可执行入口”为准，不写假成功。

**6. markdown-nice**

目标：主题样式和公众号/知乎排版参考。

真实使用方式：

- 项目路径：`docs/projects/markdown-nice`
- 优先读取/复用已有主题 CSS、渲染样式、Markdown converter 逻辑
- 如果没有稳定 CLI，就做“真实读取项目主题资源 + 生成 styled HTML”
- 输出：
  - `wechat-nice.html`
  - `zhihu-nice.html`
  - `tool-results/markdown-nice.json`

这里的“真实用到”标准是：必须读取项目内实际主题/样式/转换代码，并记录具体文件路径，不能只写“参考 markdown-nice”。

**7. adapter 验收**

每个 adapter 必须有测试：

- 项目不存在时：记录 unavailable。
- 项目存在但命令失败：记录 failed。
- 项目成功：`used_real_project = true`。
- 禁止命令被请求时：直接拒绝，不能执行。
- 所有 stdout/stderr 截断写入，不污染主输出。

这块工具 adapter 设计对吗？确认后我继续给“深度编辑链设计”。

---

**设计 4：深度编辑链**

这部分是升级质量的核心。目标是让视频脚本变成真正的文章，而不是“清理过的视频稿”。

新增 5 个阶段。

**1. 内容诊断**

输入：原始 Markdown、解析结构、保护区信息。

输出：

```text
analysis/content-diagnosis.md
```

诊断必须回答：

- 核心主张是什么
- 哪些是视频制作指令，要删
- 哪些是口播内容，可保留
- 哪些段落需要扩写解释
- 哪些地方过于口号化
- 哪些地方缺案例
- 哪些地方缺反例或边界
- 哪些地方适合配图或动图
- 微信读者的阅读阻力是什么
- 知乎读者的阅读阻力是什么

**2. 平台编辑计划**

分别输出：

```text
analysis/wechat-edit-plan.md
analysis/zhihu-edit-plan.md
```

微信计划偏：

```text
现场感
短段落
强开头
故事推进
类比
情绪节奏
结尾行动感
```

知乎计划偏：

```text
先结论
概念定义
论证链
反例
边界条件
可操作步骤
```

计划必须是段落级的，不是泛泛而谈。例如：

```text
原第 3 节：保留核心观点，但要补一个真实项目里的失败例子。
原第 5 节：压缩 30%，避免口播重复。
原第 7 节：改成“三步操作法”，适合知乎读者收藏。
```

**3. 深度改写**

输出：

```text
drafts/wechat-deep-draft.md
drafts/zhihu-deep-draft.md
```

改写规则：

- 不能虚构事实。
- 可以扩写解释，但必须来自原文逻辑。
- 可以重排结构。
- 可以删口播废话。
- 可以补“解释型过渡”，但不能补不存在的案例。
- 保留项目名、代码、命令、链接、数字、专有名词。
- 每篇文章都必须独立可读，不依赖视频语境。

**4. 风格校准**

调用 `kazike-writing-style`，但只作为方法，不套固定句。

校准点：

```text
事件现场
个人实践
过程数字
失败细节
机制解释
趋势判断
普通人行动
```

如果原文没有数据，不能编数字；只能提醒“缺少可引用过程数字”。

输出：

```text
drafts/wechat-reviewed.md
drafts/zhihu-reviewed.md
analysis/style-calibration.md
```

**5. 内容质量复审**

复审要产出：

```text
reviews/editor-review.md
reviews/platform-review.md
```

检查项：

- 是否还有脚本腔
- 是否有视频制作痕迹
- 是否有空泛口号
- 是否每个抽象概念有解释或例子
- 是否主线清楚
- 是否微信和知乎结构真的不同
- 是否平台调性匹配
- 是否配图点足够
- 是否有事实漂移

如果复审不过，不进入最终渲染。

**核心实现方式**

这里不能完全靠 Python 规则脚本。建议做成“脚本生成任务包，Codex 执行编辑任务”。

也就是：

```text
article_publish.py --deep-rewrite
```

会生成：

```text
editorial-task.md
protected-spans.json
source-structure.json
```

然后 Codex 按 task 生成深度稿。脚本再继续跑工具链和验收。

这样做的好处是：

- 深度写作交给模型
- 结构和证据交给脚本
- 输出可追溯
- 测试能覆盖任务包和验收，不要求 Python 自己写出好文章

**质量门槛**

第一版建议设置硬门槛：

- 微信稿不少于原有效口播内容的 80%，但可以重组。
- 知乎稿必须包含“先说结论”或等价结论段。
- 方法论文章至少包含 3 个可执行步骤。
- 每 1200-1800 字至少一个视觉点。
- 不允许出现 `画面建议`、`口播`、`屏幕字幕`、`拍摄备注` 等脚本标签。
- 不允许出现未经原文支持的新案例、新数据、新身份背书。

这块深度编辑链对吗？确认后我继续给“媒体与 Image Gen / Remotion 设计”。

---


**设计 5：媒体、Image Gen 与 Remotion**

这部分要解决你前面提到的“配图太少”和“动图只是 brief”的问题。

**1. 媒体规划从固定 1 张改成结构驱动**

新增：

```text
media/media-slots.json
media/image-prompts.json
media/motion-plan.json
media/media-plan.md
```

`media-slots.json` 结构：

```json
[
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
]
```

**2. 配图数量规则**

默认规则：

- 1000 字以下：封面 + 1 张正文图
- 1000-3000 字：封面 + 2 张正文图
- 3000-6000 字：封面 + 3-5 张正文图
- 6000 字以上：封面 + 每 1200-1800 字 1 张图
- 方法论文章：必须至少有
  - 总览图
  - 流程图
  - 对照图
- 如果原文有复杂流程：必须生成 1 个 Remotion 动图计划

这篇 Vibe 方法论文章合理目标是：

```text
cover
figure-01-overview：AI 问题解决闭环总览
figure-02-research-map：未知领域调研地图
figure-03-agent-parallel：多 agent 并行工作台
figure-04-verification-loop：双模型反驳与验收闭环
motion-01-loop：8 秒问题解决闭环动图
```

**3. Image Gen 调用方式**

流程：

```text
media-slots.json
-> image-prompts.json
-> 调用 imagegen skill
-> 保存到 assets/
-> 替换 wechat/zhihu 中对应占位
-> report.json 记录生成源和目标路径
```

每张图必须有：

- 用途
- 插入位置
- prompt
- 输出文件名
- 验收标准
- 是否已替换进文章

避免只生成一张“万能信息图”。

**4. Remotion 设计**

Remotion 第一版不强制渲染所有动图，但要比现在更完整。

新增：

```text
media/remotion/
├── motion-plan.json
├── storyboard.md
├── props.json
└── render-status.json
```

如果用户开启 `--render-motion`，才真实创建/调用 Remotion 项目渲染：

```text
media/remotion/preview.gif
media/remotion/preview.mp4
```

默认只生成完整可执行 brief，不声称已经渲染。

**5. 媒体验收**

发布前检查必须确认：

- 每个 required image slot 都有图片或明确 fallback。
- 文章中没有未替换占位图。
- 图片文件存在。
- 图片尺寸适合平台。
- 公众号和知乎首图不同需求被考虑。
- report 中 `media.assets[].status` 不能撒谎：
  - `planned`
  - `generated`
  - `reused`
  - `failed`
  - `brief_only`

**6. 开源项目与媒体的关系**

- `markdown-nice`：检查图片在主题 HTML 中的显示效果。
- `md2wechat`：检查公众号 HTML 中图片顺序、路径、样式。
- `Wenyan`：检查平台转换后图片是否保留。
- `lint` 工具：不负责图片生成，但可检查 Markdown 图片 alt、路径、空链接。

这块媒体设计对吗？确认后我继续给“最终产物、报告和验收标准设计”。

---

**设计 6：最终产物、报告与验收**

最终包建议从现在的“发布文件集合”升级成“可审计发布包”。

目录结构：

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
│   ├── cover.png
│   ├── figure-01-overview.png
│   ├── figure-02-research-map.png
│   └── ...
├── analysis/
│   ├── source-structure.json
│   ├── protected-spans.json
│   ├── content-diagnosis.md
│   ├── wechat-edit-plan.md
│   ├── zhihu-edit-plan.md
│   └── style-calibration.md
├── drafts/
│   ├── wechat-deep-draft.md
│   ├── zhihu-deep-draft.md
│   ├── wechat-reviewed.md
│   └── zhihu-reviewed.md
├── media/
│   ├── media-slots.json
│   ├── image-prompts.json
│   ├── media-plan.md
│   └── remotion/
│       ├── motion-plan.json
│       ├── storyboard.md
│       ├── props.json
│       └── render-status.json
├── tool-results/
│   ├── lint-md.json
│   ├── textlint-wechat.json
│   ├── textlint-zhihu.json
│   ├── zhlint-wechat.json
│   ├── zhlint-zhihu.json
│   ├── md2wechat.json
│   ├── wenyan.json
│   └── markdown-nice.json
├── reviews/
│   ├── editor-review.md
│   ├── platform-review.md
│   └── subagent-review.md
├── logs/
│   ├── lint.json
│   ├── tool-availability.json
│   └── pipeline.log
├── publish-checklist.md
└── report.json
```

**report.json 必须升级**

核心字段：

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

**publish-checklist.md 升级**

不再只是图片和标题检查，要包含：

- 标题
- 摘要
- 封面
- 首图
- 正文图数量
- 外链
- 代码块
- 工具链结果
- 文本质量
- 平台预览
- 未执行事项：上传/草稿/发布

**质量门槛**

硬门槛：

- 四个最终稿文件存在。
- 无脚本标签残留。
- 所有本地图片都存在。
- required media slots 全部解决。
- `lint-md/textlint/zhlint` 至少完成或明确失败并记录原因。
- `md2wechat` 至少对微信稿做一次安全转换/预览。
- `markdown-nice` 至少真实读取主题/样式并生成一个 styled HTML。
- `Wenyan` 如无可用 CLI，必须明确记录不可用原因。
- subagent review 必须通过。
- `report.json` 不能出现“planned 但实际已引用”的不一致状态。

软门槛：

- 微信稿开头有现场感。
- 知乎稿第一屏有清晰结论。
- 每个抽象概念至少有解释、案例或边界。
- 不堆模板句。
- 配图和正文位置匹配。
- 文章能独立阅读，不依赖视频。

**失败处理**

如果某个开源工具失败：

- 不中断整条链路。
- 写入 `tool-results/<tool>.json`。
- `report.json` 标记 `failed`。
- 使用 fallback 产物继续。
- checklist 明确提示“该工具未成功参与最终产物”。

但如果所有关键工具都没真正用上，本轮任务不能验收。

这块最终产物和验收设计对吗？确认后我会把完整方案写成 spec 文档。
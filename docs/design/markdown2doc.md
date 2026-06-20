查了一圈，比较适合你的不是单个工具，而是一套组合。

**最接近你需求的工具**
1. [文颜 Wenyan](https://github.com/caol64/wenyan)  
最贴近“Markdown 原文 -> 公众号/知乎/头条等平台格式”的需求。它支持微信公众号、知乎、今日头条等平台，也有 CLI、MCP、核心库，适合后面接进 Agent 工作流。  
我会优先看它。

2. [md2wechat-skill / md2wechat](https://github.com/geekjourneyx/md2wechat-skill)  
偏微信公众号自动发布。它主打 Markdown 转微信可用 HTML、本地预览、图片上传、封面、推送草稿箱，而且明确面向 Claude Code / Codex 这类 Agent。  
如果你的重点是公众号自动化发布，这个最像“技能”。

3. [doocs/md](https://github.com/doocs/md)  
成熟的微信 Markdown 编辑器，支持 Markdown、数学公式、Mermaid、代码高亮、多图床、AI 助手等。适合人工预览和复制到公众号后台。  
缺点是更像编辑器，不是完整自动发布链路。

4. [mdnice/markdown-nice](https://github.com/mdnice/markdown-nice)  
老牌 Markdown 排版工具，支持微信公众号、知乎、掘金。主题生态不错，适合做“文章最终排版效果”。  
但自动化程度不如 CLI 工具。

5. [Wechatsync](https://github.com/wechatsync/Wechatsync)  
浏览器扩展，主打一键同步文章到多个平台，支持微信公众号文章同步到知乎、头条、掘金等 29+ 平台。它不是 Markdown 排版器，更像发布/同步层。

**内容检查这块**
排版工具一般不负责“内容质量检查”。可以接这些：

- [textlint](https://github.com/textlint/textlint)：自然语言 lint 框架。
- [textlint-rule-preset-zh-technical-writing](https://github.com/darkyzhou/textlint-rule-preset-zh-technical-writing)：中文技术写作规则预设。
- [lint-md](https://github.com/lint-md/lint-md)：检查中文 Markdown 格式规范。
- [zhlint](https://github.com/zhlint-project/zhlint)：中文文本 lint，支持 Markdown。
- [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)：中英文空格、标点、排版规范参考。

**我建议你的工作流**
```text
原始 Markdown
-> shuorenhua 去 AI 味/润色
-> lint-md / textlint 做格式和中文写作检查
-> 检查图片路径、封面、标题、摘要、链接
-> 文颜输出知乎/公众号适配版本
-> md2wechat 推公众号草稿箱
-> Wechatsync 或手动发布到知乎
```

**如果只选一个方向**
- 想“多平台排版”：选 **文颜**。
- 想“公众号自动发布”：选 **md2wechat-skill**。
- 想“稳定人工预览”：选 **doocs/md** 或 **mdnice**。
- 想“内容检查”：自己组合 **shuorenhua + textlint/lint-md**。

对你现在这个 `yy-article` 工作流，我更建议做一个本地 `article-publish` skill：输入 Markdown，自动跑润色、检查、封面/图片检查，然后输出 `wechat.html`、`zhihu.md`、发布检查清单。这样比单纯依赖某个编辑器更贴合你现在的写作方式。

---


可以用进 skill 里的，按适配度大概这样分：

**最适合直接集成**
1. [文颜 Wenyan](https://github.com/caol64/wenyan)  
适合放进 skill 作为核心排版转换层：`Markdown -> 微信/知乎/头条等平台格式`。如果它的 CLI 或核心库稳定，skill 可以直接调用它生成平台版本。

2. [md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill)  
它本身就是面向 Agent 的 skill 思路，适合参考或直接拆能力：公众号排版、图片处理、草稿箱推送。  
如果你重点做微信公众号发布，这个最值得借鉴。

3. [textlint](https://github.com/textlint/textlint)  
适合放进 skill 的“内容检查”阶段。可以检查重复表达、标点、写作规则。

4. [textlint-rule-preset-zh-technical-writing](https://github.com/darkyzhou/textlint-rule-preset-zh-technical-writing)  
适合配合 textlint，用来检查中文技术写作问题。

5. [lint-md](https://github.com/lint-md/lint-md)  
适合检查 Markdown 格式、中英文空格、标点、列表等。

6. [zhlint](https://github.com/zhlint-project/zhlint)  
也适合做中文排版 lint，不过规则风格要测试一下，避免误伤你的文章语气。

**适合参考，不太适合直接做自动化核心**
1. [doocs/md](https://github.com/doocs/md)  
适合参考它的微信样式、主题、预览逻辑。它更像在线编辑器，不是最适合作为 skill 的自动化执行层。

2. [mdnice/markdown-nice](https://github.com/mdnice/markdown-nice)  
适合参考主题 CSS、排版样式、多平台适配经验。直接接进 skill 也可以，但要看它有没有稳定 CLI/API；否则更适合作为样式来源。

**不太适合放进 skill 内部**
1. [Wechatsync](https://github.com/wechatsync/Wechatsync)  
它是浏览器扩展，适合人工发布/同步阶段，不适合做 Codex skill 的核心自动化。除非你愿意走浏览器自动化，否则不建议放进 skill。

**我建议这个 skill 的能力拆法**
```text
article-publish skill

1. 输入 Markdown
2. shuorenhua 润色
3. textlint / lint-md / zhlint 检查
4. 检查标题、摘要、封面、图片路径、外链
5. Wenyan 生成知乎版/公众号版
6. 可选：md2wechat 推公众号草稿箱
7. 输出发布前检查清单
```

如果只做第一版，我建议集成这几个：

- `shuorenhua`：润色去 AI 味
- `lint-md`：Markdown 和中文排版检查
- `textlint + zh technical writing preset`：内容规则检查
- `Wenyan`：多平台排版输出
- `md2wechat-skill`：公众号发布能力参考或二期接入

这样这个 skill 会比单纯“排版工具”更完整，能覆盖你真正需要的：**润色、检查、排版、导出、发布前验收**。
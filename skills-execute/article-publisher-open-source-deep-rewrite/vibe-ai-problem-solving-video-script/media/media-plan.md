# Media Plan

Source: `/Users/apulu/Documents/yy-article/write-v2/vibe-ai-problem-solving-video-script.md`

## Assets

### cover

- Type: `image`
- Executor: `existing_asset`
- Output: `assets/cover-ai-vibe-workbench.png`
- Status: `planned`
- Prompt: 复用文章已有首图或封面图，并在发布前检查裁切、清晰度和平台预览。

### figure-01-overview

- Type: `image`
- Executor: `codex_image_gen`
- Output: `assets/figure-01-overview.png`
- Status: `planned`
- Prompt: 为中文文章《Vibe 方法论：如何利用 AI 快速高效解决真实问题》生成一张 16:9 信息图。用途：解释全文核心观点总览。依据正文片段：我现在更愿意把 Vibe Coding 理解成一个工作台，而不是一种玄学状态。 它真正有价值的地方，不是让模型连续生成很多内容，而是把一个真实问题拆成几段：先看清楚，再做一个最小版本，再找另…。画面清晰、现代、克制，适合微信公众号和知乎正文插图；不要伪文字、水印和品牌标识。

### figure-02-flow

- Type: `image`
- Executor: `codex_image_gen`
- Output: `assets/figure-02-flow.png`
- Status: `planned`
- Prompt: 为中文文章《Vibe 方法论：如何利用 AI 快速高效解决真实问题》生成一张 16:9 信息图。用途：解释关键流程或步骤。依据正文片段：有一次链路看起来已经完成了：页面能点，接口有返回，测试也是绿的。 但反方模型追问了一个问题：这个测试有没有绕过真实上传、真实任务触发和真实产物写入？如果 fake client 自己制造输入…。画面清晰、现代、克制，适合微信公众号和知乎正文插图；不要伪文字、水印和品牌标识。

### figure-03-comparison

- Type: `image`
- Executor: `codex_image_gen`
- Output: `assets/figure-03-comparison.png`
- Status: `planned`
- Prompt: 为中文文章《Vibe 方法论：如何利用 AI 快速高效解决真实问题》生成一张 16:9 信息图。用途：解释错误做法和正确做法的对照。依据正文片段：模型越来越强以后，很多玄学 prompt 确实没那么重要了。但需求表达更重要了。 好的 prompt 不靠身份扮演堆气势，而是把背景、目标、边界、输入材料、输出格式、验收标准讲清楚。 我更常…。画面清晰、现代、克制，适合微信公众号和知乎正文插图；不要伪文字、水印和品牌标识。

### figure-04-verification

- Type: `image`
- Executor: `codex_image_gen`
- Output: `assets/figure-04-verification.png`
- Status: `planned`
- Prompt: 为中文文章《Vibe 方法论：如何利用 AI 快速高效解决真实问题》生成一张 16:9 信息图。用途：解释验证、反驳或复盘闭环。依据正文片段：下次你要用 AI 做一个真实项目，可以先按这几个问题往下问： - 目标：我要解决的真实问题是什么？ - 地图：这个领域通常怎么拆？最小版本是哪一刀？ - 上下文：模型需要哪些文件、日志、代码…。画面清晰、现代、克制，适合微信公众号和知乎正文插图；不要伪文字、水印和品牌标识。

### motion-01

- Type: `animated_explainer`
- Executor: `remotion`
- Output: `media/remotion/preview.gif`
- Status: `brief_only`
- Prompt: 制作 6-8 秒动态图，解释《Vibe 方法论：如何利用 AI 快速高效解决真实问题》的核心观点。使用 16:9，24fps，字幕简洁，适合文章开头嵌入。

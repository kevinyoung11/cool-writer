# 寻找视频脚本开源方案

> 如果我想根据想法和素材写一个视频脚本，社区里或者开源方案里，有什么比较好的方案可以实现吗？

<details><summary>2 previous messages</summary>

> 我会先查一下近期社区里还活跃的开源/半开源方案，重点看能否把“想法 + 素材”转成可拍/可剪的视频脚本，而不是只做通用聊天。
>
> <details><summary>Explored 2 files, searched the web</summary>
>
> <details><summary>Explored 2 files</summary>
>
> - Read `~/.codex/superpowers/skills/using-superpowers/SKILL.md`
> - Read `~/.codex/superpowers/skills/brainstorming/SKILL.md`
>
> </details>
>
> <details><summary>Searched the web</summary>
>
> - Searched the web for `open source AI video script generator from idea materials LLM workflow 2026`
> - Searched the web for `Dify open source LLM app workflow knowledge base documents official`
> - Searched the web for `site:github.com open source storyboard AI script generator video "storyboard" "script"`
>
> </details>
>
> </details>
</details>

可以实现，而且我建议别一开始找“视频脚本生成器”成品，而是按工作流搭：**素材整理/RAG → 结构化提纲 → 脚本 → 分镜/镜头表 → 口播稿/画面提示词**。这样可控性最好。

**优先推荐方案**

1. **Dify：最适合快速做成可用工具**
   Dify 是开源 LLM 应用平台，支持工作流、知识库/RAG、Agent、模型管理；官方也在做多模态知识库，文本和图片素材可以一起检索使用。适合你把文章、笔记、链接、图片说明、产品资料放进去，然后输出固定格式的视频脚本。
   来源：[Dify GitHub](https://github.com/langgenius/dify)、[Dify 多模态知识库](https://dify.ai/blog/multimodal-retrieval-is-now-available-in-the-knowledge-base)

2. **n8n：适合做自动化流水线**
   n8n 适合把素材入口接起来，比如表单、Notion、Google Drive、RSS、网页、字幕、数据库，然后自动跑“提取素材 → 生成脚本 → 发到文档/表格/飞书/Notion”。它是 fair-code，不是严格 OSI 意义上的纯开源，但社区生态很强。
   来源：[n8n GitHub](https://github.com/n8n-io/n8n)、[n8n AI workflow docs](https://docs.n8n.io/advanced-ai/intro-tutorial/)

3. **LangGraph：适合自己写一个更稳定的脚本 Agent**
   如果你想做得更工程化，比如多轮改稿、风格记忆、素材引用、人工审核节点、脚本评分，LangGraph 更合适。它适合把流程拆成多个节点：素材分析、选题判断、标题钩子、结构生成、逐段写作、审核、重写。
   来源：[LangGraph](https://www.langchain.com/langgraph)、[LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview)

**偏视频/分镜方向的开源项目**

- **Toonflow**：开源一站式 AI 短剧创作工具，覆盖剧本、分镜、角色、视频生成，更偏短剧/动画短片。
  来源：[GitHub topic: text-to-video](https://github.com/topics/text-to-video)

- **ViMax**：偏“概念到视频”的 agentic video generation，包含编剧、分镜、角色和视频生成；适合研究端到端流程，不一定适合直接当生产工具。
  来源：[ViMax GitHub](https://github.com/HKUDS/ViMax)

- **StoryGen Atelier**：Gemini 生成分镜文本和画面，Vertex AI Veo 生成过渡视频，ffmpeg 拼接；适合参考“脚本到分镜到视频”的工程结构。
  来源：[StoryGen Atelier GitHub](https://github.com/0xsline/StoryGen-Atelier)

- **Storyboard AI / AI-storyboard-generator 类项目**：更偏把脚本转成分镜、镜头描述、画面提示词。适合做视频脚本后半段。
  来源：[Storyboard AI GitHub](https://github.com/yogendra-yatnalkar/storyboard-ai)、[AI storyboard GitHub topic](https://github.com/topics/ai-storyboard)

**我会怎么选**

如果你的目标是“根据想法和素材，稳定产出可拍/可剪的视频脚本”，我建议：

- **轻量版**：Dify + 知识库 + 固定输出模板。
- **自动化版**：n8n + Dify/LLM API，把素材入口和文档输出接起来。
- **可产品化版**：LangGraph + 向量库 + 人工审核界面。
- **短剧/AI 视频版**：参考 Toonflow、ViMax、StoryGen Atelier，但不要完全依赖它们，更多是借鉴流程。

脚本输出格式可以固定成：

```text
选题定位
目标观众
核心观点
开头 3 秒钩子
30/60/90 秒版本
逐镜头分镜
口播稿
画面说明
字幕文案
B-roll/素材引用
剪辑节奏
结尾 CTA
```

如果只是给自己用，最快的落地方案就是 **Dify 工作流**。如果你想把它做成一个可长期复用的小工具，我更建议 **LangGraph + 简单 Web UI**。

> 我现在仅仅是想做写视频脚本的能力，不是别的

明白，那就不要碰“脚本到视频”“分镜生成”“自动剪辑”这些。你现在要的是一个能力：

> 输入：想法 + 素材
> 输出：可用的视频脚本

最合适的方案是做一个**视频脚本写作工作流**，而不是找完整 AI 视频工具。

我建议优先看这三类：

**1. Dify：最适合快速搭一个脚本生成器**

适合你现在这个阶段。
可以做成：

```text
输入想法
上传/粘贴素材
选择视频类型：口播 / 短视频 / 访谈 / 解说 / 带货 / 知识类
选择时长：30 秒 / 1 分钟 / 3 分钟 / 5 分钟
输出脚本
```

Dify 的好处是有界面、有工作流、有知识库，适合把素材喂进去，再按固定模板生成脚本。

**2. LangGraph：适合做成更强的写作 Agent**

如果你想让脚本质量更稳定，可以拆成几个步骤：

```text
素材理解
↓
提炼核心观点
↓
确定受众和视频目标
↓
生成结构
↓
写开头钩子
↓
写完整脚本
↓
自检：是否啰嗦、是否跑题、是否有爆点
↓
重写优化
```

这类更适合你以后做成自己的“脚本写作助手”。

**3. 纯 Prompt + 模板：如果只是个人使用，最快**

其实你现在不一定需要开源系统。先沉淀一套结构化 Prompt 就够了，比如：

```text
你是一个短视频脚本策划。
请根据我提供的想法和素材，生成一个视频脚本。

要求：
1. 先判断素材里的核心观点
2. 给出 3 个可选切入角度
3. 选择最适合短视频传播的角度
4. 输出完整脚本

输出格式：
- 标题
- 视频定位
- 目标观众
- 开头 3 秒钩子
- 正文口播稿
- 画面建议
- 字幕重点
- 结尾引导
- 可删减版本
```

我的建议是：

如果你只是自己写脚本，先用 **Prompt 模板**。
如果你想做成一个稳定工具，用 **Dify**。
如果你想做成一个可持续进化的“脚本写作能力”，用 **LangGraph**。

关键不是选哪个开源项目，而是把能力拆成这几个模块：

```text
素材读取 → 观点提炼 → 选题角度 → 脚本结构 → 口播文案 → 自检重写
```

这就是“写视频脚本”的核心链路。

> 有开源方案比较好的吗，能让脚本写的比较深入且好，

<details><summary>2 previous messages</summary>

> 我会把范围收窄到“能提升脚本深度和质量的开源写作/Agent/RAG框架”，不看那些一站式视频生成项目。重点会比较：是否支持素材扎实引用、分步骤写作、反思改稿、可控输出格式。
>
> <details><summary>Searched the web</summary>
>
> <details><summary>Searched the web</summary>
>
> - Searched the web for `open source AI writing agent framework RAG long form script writing GitHub 2026`
> - Searched the web for `CrewAI open source multi agent framework official GitHub`
> - Searched the web for `promptfoo open source LLM eval official GitHub`
>
> </details>
>
> </details>
</details>

有，但我会把“好”定义清楚：**不是某个开源项目天生会写好脚本，而是它能不能支撑一套深度写作流程**。

如果只做“写视频脚本能力”，我最推荐这几个开源方向：

**1. LangGraph：最推荐，适合做高质量脚本写作流程**

适合你要“深入且好”的脚本。
因为视频脚本质量通常不是一次生成出来的，而是多步打磨：

```text
素材理解
→ 主题判断
→ 受众判断
→ 角度选择
→ 结构设计
→ 初稿
→ 事实/逻辑检查
→ 节奏优化
→ 金句/标题/开头重写
```

LangGraph 的优势是可以把这些步骤做成稳定流程，而不是一条 Prompt 硬怼。它官方定位就是做可控的 agent/workflow，适合有分支、有循环、有反思改稿的任务。

来源：[LangGraph](https://www.langchain.com/langgraph)、[LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview)

**2. LlamaIndex：适合“基于素材写得深”**

如果你的素材很多，比如文章、录音稿、网页、PDF、访谈、笔记，LlamaIndex 很适合做素材层。它强在数据接入、索引、检索、RAG，让脚本不是凭空写，而是围绕素材提炼。

可以搭配 LangGraph：

```text
LlamaIndex 负责读素材、找证据、提炼信息
LangGraph 负责组织写作流程和反复改稿
```

来源：[LlamaIndex GitHub](https://github.com/run-llama/llama_index)、[LlamaIndex docs](https://developers.llamaindex.ai/python/framework/)

**3. Haystack：适合更工程化的 RAG 脚本系统**

Haystack 也适合“素材驱动写作”，它偏生产级 RAG pipeline，可以明确控制检索、路由、记忆、生成。
如果你后面想做一个稳定服务，而不是个人脚本工具，Haystack 值得考虑。

来源：[Haystack GitHub](https://github.com/deepset-ai/haystack)、[Haystack docs](https://docs.haystack.deepset.ai/docs/intro)

**4. GPT Researcher / Open Deep Research：适合补“研究深度”**

如果你的视频脚本需要外部调研，比如知识类、商业分析、科技评论、人物故事，可以把它作为“研究员”模块。它先产出带来源的研究材料，再交给脚本写作流程改成视频语言。

来源：[GPT Researcher](https://github.com/assafelovic/gpt-researcher)、[Open Deep Research](https://github.com/langchain-ai/open_deep_research)

**5. Dify：适合先做 MVP，但深度上限不如代码工作流**

Dify 可以快速搭一个“输入素材 → 生成脚本”的工具，有工作流、知识库、界面。
如果你不想先写代码，Dify 是最快的；但如果你追求“脚本长期稳定变好”，最终可能还是会走 LangGraph / LlamaIndex 这种代码化流程。

来源：[Dify GitHub](https://github.com/langgenius/dify)

我的排序是：

```text
个人快速验证：Dify
认真做脚本能力：LangGraph + LlamaIndex
素材特别重：LlamaIndex / Haystack
研究型视频：GPT Researcher + LangGraph
```

如果目标是“脚本写得深入且好”，我会选：

```text
LangGraph + LlamaIndex + Promptfoo
```

其中 Promptfoo 用来测试不同 Prompt、不同模型、不同流程的输出质量，避免只靠感觉判断哪版脚本更好。
来源：[Promptfoo](https://github.com/promptfoo/promptfoo)

最小可行架构可以是：

```text
输入想法/素材
→ 素材摘要
→ 核心观点提炼
→ 选 3 个切入角度
→ 评估哪个角度最有传播力
→ 生成脚本大纲
→ 写完整口播稿
→ 检查：是否有洞察、是否空泛、是否重复、是否适合视频表达
→ 输出最终脚本
```

结论：**没有必要找“视频脚本生成器”成品。最好的开源方案是用 LangGraph 搭写作流程，用 LlamaIndex/Haystack 管素材，用 Promptfoo 做质量评估。**

> 如果说围绕这个来设计，给我设计一个比较好的方案，要足够细节

可以。下面这个方案只围绕一件事：**把“想法 + 素材”稳定写成深入、可用、有观点的视频脚本**。不做生成视频、不做剪辑、不做分镜图。

**总体定位**
做一个“视频脚本写作引擎”，核心不是聊天，而是一个多阶段写作流程：

```text
想法/选题
+ 素材
+ 目标受众
+ 视频类型
+ 时长
→ 观点提炼
→ 角度选择
→ 结构设计
→ 初稿
→ 深度增强
→ 视频化改写
→ 质量评审
→ 终稿
```

我建议技术方案用：

```text
LangGraph：编排写作流程
LlamaIndex：管理和检索素材
PostgreSQL / SQLite：保存项目、脚本版本、评分
Chroma / Qdrant：向量检索素材
Promptfoo：测试脚本质量和 Prompt 效果
简单 Web UI：输入素材、选择风格、查看多版脚本
```

参考项目：
[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)、[LlamaIndex](https://github.com/run-llama/llama_index)、[Promptfoo](https://github.com/promptfoo/promptfoo)

**核心能力设计**
系统不要直接说“请帮我写一个脚本”。要拆成 8 个节点。

**1. 素材理解节点**

输入可以是：

```text
一句想法
文章
网页内容
访谈稿
语音转文字稿
产品资料
个人笔记
历史爆款脚本
```

输出不是脚本，而是素材卡片：

```json
{
  "core_facts": ["事实1", "事实2"],
  "strong_opinions": ["可发展的观点"],
  "useful_examples": ["案例"],
  "emotional_hooks": ["冲突", "反差", "痛点"],
  "quotable_lines": ["适合改成金句的句子"],
  "missing_context": ["还缺什么信息"]
}
```

这一步决定脚本深不深。很多脚本浅，是因为模型没有先把素材拆透。

**2. 选题诊断节点**

判断这个想法适合拍什么类型的视频：

```text
知识解释型
观点评论型
故事叙事型
产品介绍型
经验复盘型
热点分析型
带货转化型
个人 IP 型
```

输出：

```json
{
  "video_type": "观点评论型",
  "target_audience": "对 AI 工具感兴趣但还没形成方法论的人",
  "viewer_question": "我为什么要看这个视频？",
  "core_promise": "看完知道如何搭一个更靠谱的视频脚本生成系统",
  "risk": "容易讲成工具清单，缺少判断"
}
```

**3. 角度生成节点**

同一个素材至少生成 3 个切入角度：

```text
角度 A：问题导向
角度 B：反常识导向
角度 C：故事导向
```

每个角度都要评分：

```json
{
  "angle": "不要找视频生成器，要搭写作流程",
  "novelty": 8,
  "depth": 9,
  "audience_pull": 7,
  "material_support": 8,
  "reason": "更符合用户真实问题，也避免空泛工具推荐"
}
```

最终选一个主角度，保留两个备用角度。

**4. 脚本结构节点**

不要直接写正文，先生成结构。比如 3 分钟口播可以用：

```text
0-5 秒：钩子
5-20 秒：提出问题
20-60 秒：拆解误区
60-130 秒：给出方法
130-165 秒：举例
165-180 秒：总结和行动建议
```

输出结构化大纲：

```json
{
  "hook": "很多人想用 AI 写视频脚本，第一步就错了。",
  "thesis": "真正重要的不是找一个脚本生成器，而是搭一个写作流程。",
  "beats": [
    {
      "time": "0-5s",
      "purpose": "制造反差",
      "content": "你缺的不是 AI，而是脚本生产线。"
    }
  ]
}
```

**5. 初稿生成节点**

初稿只负责“完整”，不要负责“完美”。输出格式建议固定：

```text
标题：
一句话核心观点：
适合平台：
视频时长：
脚本正文：
画面辅助建议：
字幕重点：
结尾：
```

脚本文体要分层：

```text
口播稿：自然、像人说话
信息层：事实、案例、判断
情绪层：冲突、反差、共鸣
结构层：开头、递进、结尾
```

**6. 深度增强节点**

这是关键。让系统专门检查“有没有洞察”。

检查问题：

```text
有没有只是在罗列？
有没有明确判断？
有没有解释为什么？
有没有反例？
有没有案例？
有没有把素材中的信息转成观点？
有没有一句让人记住的话？
```

然后重写。输出一份增强说明：

```json
{
  "weaknesses": [
    "前半段像工具清单",
    "缺少为什么 LangGraph 比普通 Prompt 更适合的解释"
  ],
  "improvements": [
    "加入一次生成 vs 多阶段写作的对比",
    "加入素材驱动写作的例子"
  ],
  "rewritten_sections": ["开头", "第二段", "结尾"]
}
```

**7. 视频化改写节点**

很多 AI 写出来像文章，不像视频。这个节点专门改“可说、可听、可剪”。

规则：

```text
句子短一点
每 15-20 秒有一个推进
少用书面连接词
每段只讲一个意思
关键句适合做字幕
开头 3 秒必须有冲突
结尾要收束，不要喊口号
```

输出：

```text
口播版
字幕重点版
剪辑节奏版
```

**8. 质量评审节点**

给脚本打分，不合格就回到对应节点重写。

评分维度：

```text
观点清晰度：0-10
素材利用度：0-10
深度：0-10
开头吸引力：0-10
视频表达感：0-10
信息密度：0-10
可信度：0-10
可执行性：0-10
```

建议设置门槛：

```text
总分低于 75：重写
深度低于 7：回到深度增强节点
素材利用低于 7：回到素材理解节点
开头低于 7：只重写开头
```

**产品形态**
最小版本可以很简单：

```text
左侧：输入想法和素材
中间：选择视频类型、时长、风格
右侧：输出脚本
底部：质量评分、修改建议、重新生成按钮
```

核心按钮：

```text
生成角度
生成大纲
生成脚本
增强深度
改成更口语
生成 30 秒版
生成 3 分钟版
只重写开头
只重写结尾
```

**数据结构**
每个项目保存这些东西：

```json
{
  "project_id": "xxx",
  "idea": "用户原始想法",
  "materials": [],
  "audience": "目标观众",
  "platform": "抖音 / B站 / 视频号 / YouTube",
  "duration": "3min",
  "style": "理性、有观点、口语化",
  "angles": [],
  "outline": {},
  "drafts": [],
  "final_script": "",
  "scores": []
}
```

**Prompt 资产**
你需要维护几类 Prompt，而不是一个大 Prompt：

```text
material_analyzer_prompt
angle_generator_prompt
outline_writer_prompt
draft_writer_prompt
depth_rewriter_prompt
video_language_rewriter_prompt
script_judge_prompt
```

这样后面容易单独优化。比如脚本不够深，只改 `depth_rewriter_prompt`，不用动全部流程。

**质量样本库**
如果你想让它越写越好，需要建一个“好脚本样本库”：

```text
优秀开头
优秀转折
优秀结构
优秀结尾
不同平台脚本
你的个人风格样本
你不喜欢的反例
```

每次生成脚本前，系统先检索相似样本，作为风格参考。

**推荐 MVP**
第一版不要做太大，只做 5 个节点：

```text
素材理解
→ 角度选择
→ 大纲
→ 脚本初稿
→ 质量评审 + 重写
```

用 Dify 也能先验证；但如果你确定要长期做，我建议直接用 LangGraph，因为后面“循环改稿”和“按评分回退”更自然。

**最终效果**
用户输入：

```text
我想讲 AI 写视频脚本，素材是这些工具和我的想法……
```

系统输出的不只是脚本，而是：

```text
3 个切入角度
推荐角度及理由
结构大纲
完整口播稿
字幕重点
脚本评分
修改建议
最终优化版
```

这套设计的核心判断是：**好脚本不是生成出来的，是经过“理解、选择、组织、写作、审稿、重写”生产出来的。**
